"""
Multi-Agent System Orchestrator

This module coordinates the execution of all three agents in the product
listing generation pipeline, managing data flow, error handling, and
result aggregation.
"""

import asyncio
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

# Handle both package imports and direct execution
try:
    from .agents.base_agent import BaseAgent, AgentFactory, AgentException
    from .models.data_models import (
        ProductInput, PipelineResult, AgentResult, AgentType,
        StageStatus, SystemConfig, AgentConfig
    )
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    from agents.base_agent import BaseAgent, AgentFactory, AgentException
    from models.data_models import (
        ProductInput, PipelineResult, AgentResult, AgentType,
        StageStatus, SystemConfig, AgentConfig
    )

class ProductListingOrchestrator:
    """
    Main orchestrator that coordinates the multi-agent workflow for
    automated product listing generation.

    Workflow stages:
    1. Product Description Generation (web scraping + AI enhancement)
    2. Image Generation (nano-banana API integration)
    3. E-commerce Integration (Shopify formatting)
    """

    def __init__(self, config: SystemConfig, logger: Optional[logging.Logger] = None):
        """
        Initialize the orchestrator with system configuration.

        Args:
            config: System-wide configuration
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger(self.__class__.__name__)

        # Initialize agents
        self.agents: Dict[AgentType, BaseAgent] = {}
        self._initialize_agents()

        # Execution settings
        self.max_concurrent_agents = config.max_concurrent_agents
        self.pipeline_timeout = config.default_timeout * 3  # Total pipeline timeout

        # Results storage
        self.active_pipelines: Dict[str, PipelineResult] = {}

    def _initialize_agents(self) -> None:
        """Initialize all agents with their configurations."""

        # Create agent configurations
        agent_configs = {
            AgentType.DESCRIPTION_GENERATOR: AgentConfig(
                agent_type=AgentType.DESCRIPTION_GENERATOR,
                enabled=True,
                max_retries=3,
                timeout=300,
                config={
                    "openai_api_key": self.config.openai_api_key,
                    "scraping_timeout": 30,
                    "max_description_length": 5000
                }
            ),
            AgentType.IMAGE_GENERATOR: AgentConfig(
                agent_type=AgentType.IMAGE_GENERATOR,
                enabled=True,
                max_retries=2,
                timeout=180,
                config={
                    "nano_banana_api_key": self.config.nano_banana_api_key,
                    "fallback_enabled": True,
                    "image_quality_threshold": 0.7
                }
            ),
            AgentType.ECOMMERCE_INTEGRATOR: AgentConfig(
                agent_type=AgentType.ECOMMERCE_INTEGRATOR,
                enabled=True,
                max_retries=2,
                timeout=120,
                config={
                    "shopify_api_key": self.config.shopify_api_key,
                    "shopify_shop_domain": self.config.shopify_shop_domain,
                    "auto_publish": False,
                    "pod_enabled": True
                }
            )
        }

        # Override with custom configurations if provided
        for custom_config in self.config.agent_configs:
            if custom_config.agent_type in agent_configs:
                agent_configs[custom_config.agent_type] = custom_config

        # Create agent instances
        for agent_type, config in agent_configs.items():
            try:
                agent = AgentFactory.create_agent(agent_type, config, self.logger)
                self.agents[agent_type] = agent
                self.logger.info(f"Initialized {agent_type.value} agent")
            except Exception as e:
                self.logger.error(f"Failed to initialize {agent_type.value} agent: {str(e)}")
                # Continue without this agent (will be marked as skipped)

    async def execute_pipeline(self, product_input: ProductInput) -> PipelineResult:
        """
        Execute the complete product listing generation pipeline.

        Args:
            product_input: Input data for product listing generation

        Returns:
            PipelineResult containing all stage results and final output
        """

        # Create pipeline instance
        pipeline_id = str(uuid.uuid4())
        start_time = time.time()

        pipeline_result = PipelineResult(
            pipeline_id=pipeline_id,
            input_data=product_input,
            final_status=StageStatus.IN_PROGRESS
        )

        self.active_pipelines[pipeline_id] = pipeline_result

        self.logger.info(f"Starting pipeline {pipeline_id}")

        try:
            # Execute pipeline with timeout
            await asyncio.wait_for(
                self._execute_pipeline_stages(pipeline_result),
                timeout=self.pipeline_timeout
            )

            # Determine final status
            failed_stages = [r for r in pipeline_result.stage_results if r.status == StageStatus.FAILED]
            if failed_stages:
                pipeline_result.final_status = StageStatus.FAILED
                pipeline_result.error_summary = [r.error_message for r in failed_stages if r.error_message]
            else:
                pipeline_result.final_status = StageStatus.COMPLETED

        except asyncio.TimeoutError:
            pipeline_result.final_status = StageStatus.FAILED
            pipeline_result.error_summary = [f"Pipeline timeout after {self.pipeline_timeout}s"]
            self.logger.error(f"Pipeline {pipeline_id} timed out")

        except Exception as e:
            pipeline_result.final_status = StageStatus.FAILED
            pipeline_result.error_summary = [f"Unexpected error: {str(e)}"]
            self.logger.error(f"Pipeline {pipeline_id} failed: {str(e)}")

        finally:
            # Finalize results
            pipeline_result.total_execution_time = time.time() - start_time
            pipeline_result.completed_at = datetime.now()

            # Clean up
            del self.active_pipelines[pipeline_id]

            self.logger.info(
                f"Pipeline {pipeline_id} completed with status {pipeline_result.final_status.value} "
                f"in {pipeline_result.total_execution_time:.2f}s"
            )

        return pipeline_result

    async def _execute_pipeline_stages(self, pipeline_result: PipelineResult) -> None:
        """Execute all pipeline stages in sequence."""

        # Stage 1: Product Description Generation
        stage1_result = await self._execute_stage(
            AgentType.DESCRIPTION_GENERATOR,
            pipeline_result.input_data.dict()
        )
        pipeline_result.stage_results.append(stage1_result)

        if stage1_result.status != StageStatus.COMPLETED:
            self.logger.warning("Stage 1 failed, continuing with available data")
            stage1_data = {}
        else:
            stage1_data = stage1_result.data
            # Extract enhanced description
            if all(field in stage1_data for field in ["title", "detailed_description"]):
                try:
                    from .models.data_models import EnhancedProductDescription
                except ImportError:
                    from models.data_models import EnhancedProductDescription
                try:
                    pipeline_result.product_description = EnhancedProductDescription(**stage1_data)
                except Exception as e:
                    self.logger.warning(f"Could not create EnhancedProductDescription: {e}")

        # Stage 2: Image Generation (depends on Stage 1)
        stage2_input = {**pipeline_result.input_data.dict(), **stage1_data}
        stage2_result = await self._execute_stage(
            AgentType.IMAGE_GENERATOR,
            stage2_input
        )
        pipeline_result.stage_results.append(stage2_result)

        if stage2_result.status != StageStatus.COMPLETED:
            self.logger.warning("Stage 2 failed, continuing without generated image")
            stage2_data = {}
        else:
            stage2_data = stage2_result.data
            # Extract generated image
            if "image_url" in stage2_data:
                try:
                    from .models.data_models import GeneratedImage
                except ImportError:
                    from models.data_models import GeneratedImage
                try:
                    pipeline_result.generated_image = GeneratedImage(**stage2_data)
                except Exception as e:
                    self.logger.warning(f"Could not create GeneratedImage: {e}")

        # Stage 3: E-commerce Integration (depends on Stages 1 & 2)
        stage3_input = {**stage2_input, **stage2_data}
        stage3_result = await self._execute_stage(
            AgentType.ECOMMERCE_INTEGRATOR,
            stage3_input
        )
        pipeline_result.stage_results.append(stage3_result)

        if stage3_result.status == StageStatus.COMPLETED:
            # Extract Shopify listing
            try:
                from .models.data_models import ShopifyProductListing
            except ImportError:
                from models.data_models import ShopifyProductListing
            try:
                # Remove shopify_ready field for model creation
                listing_data = {k: v for k, v in stage3_result.data.items() if k != "shopify_ready"}
                pipeline_result.shopify_listing = ShopifyProductListing(**listing_data)
            except Exception as e:
                self.logger.warning(f"Could not create ShopifyProductListing: {e}")

    async def _execute_stage(self, agent_type: AgentType, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute a single pipeline stage using the specified agent.

        Args:
            agent_type: Type of agent to execute
            input_data: Input data for the agent

        Returns:
            AgentResult with execution details
        """

        if agent_type not in self.agents:
            return AgentResult(
                agent_type=agent_type,
                stage=self._get_stage_number(agent_type),
                status=StageStatus.SKIPPED,
                error_message=f"Agent {agent_type.value} not available"
            )

        agent = self.agents[agent_type]

        try:
            result = await agent.execute(input_data)
            return result

        except Exception as e:
            self.logger.error(f"Error executing {agent_type.value}: {str(e)}")
            return AgentResult(
                agent_type=agent_type,
                stage=self._get_stage_number(agent_type),
                status=StageStatus.FAILED,
                error_message=str(e)
            )

    def _get_stage_number(self, agent_type: AgentType) -> int:
        """Get stage number for agent type."""
        stage_mapping = {
            AgentType.DESCRIPTION_GENERATOR: 1,
            AgentType.IMAGE_GENERATOR: 2,
            AgentType.ECOMMERCE_INTEGRATOR: 3
        }
        return stage_mapping.get(agent_type, 0)

    async def get_pipeline_status(self, pipeline_id: str) -> Optional[PipelineResult]:
        """
        Get the current status of a running pipeline.

        Args:
            pipeline_id: Pipeline identifier

        Returns:
            PipelineResult if pipeline exists, None otherwise
        """
        return self.active_pipelines.get(pipeline_id)

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the orchestrator and all agents.

        Returns:
            Dict containing health information
        """

        agent_health = {}
        for agent_type, agent in self.agents.items():
            try:
                agent_health[agent_type.value] = agent.get_health_status()
            except Exception as e:
                agent_health[agent_type.value] = {
                    "status": "error",
                    "error": str(e)
                }

        return {
            "orchestrator": {
                "status": "healthy",
                "active_pipelines": len(self.active_pipelines),
                "agents_initialized": len(self.agents),
                "timestamp": datetime.now().isoformat()
            },
            "agents": agent_health
        }

    async def shutdown(self) -> None:
        """Gracefully shutdown the orchestrator and all agents."""

        self.logger.info("Shutting down orchestrator...")

        # Wait for active pipelines to complete (with timeout)
        if self.active_pipelines:
            self.logger.info(f"Waiting for {len(self.active_pipelines)} active pipelines to complete...")

            max_wait = 60  # seconds
            start_time = time.time()

            while self.active_pipelines and (time.time() - start_time) < max_wait:
                await asyncio.sleep(1)

            if self.active_pipelines:
                self.logger.warning(f"Force stopping {len(self.active_pipelines)} active pipelines")
                self.active_pipelines.clear()

        self.logger.info("Orchestrator shutdown complete")

class ProductListingAPI:
    """
    High-level API wrapper for the product listing system.
    Provides simple interface for common operations.
    """

    def __init__(self, config: SystemConfig):
        """Initialize the API with system configuration."""
        self.orchestrator = ProductListingOrchestrator(config)

    async def create_listing_from_url(self, product_url: str, **kwargs) -> Dict[str, Any]:
        """
        Create product listing from a URL.

        Args:
            product_url: URL to scrape product data from
            **kwargs: Additional parameters

        Returns:
            Dict containing the final product listing result
        """

        product_input = ProductInput(
            product_url=product_url,
            **kwargs
        )

        result = await self.orchestrator.execute_pipeline(product_input)

        return self._format_api_response(result)

    async def create_listing_from_description(self, title: str, description: str, **kwargs) -> Dict[str, Any]:
        """
        Create product listing from title and description.

        Args:
            title: Product title
            description: Product description
            **kwargs: Additional parameters

        Returns:
            Dict containing the final product listing result
        """

        product_input = ProductInput(
            product_title=title,
            product_description=description,
            **kwargs
        )

        result = await self.orchestrator.execute_pipeline(product_input)

        return self._format_api_response(result)

    def _format_api_response(self, pipeline_result: PipelineResult) -> Dict[str, Any]:
        """Format pipeline result for API response."""

        response = {
            "success": pipeline_result.final_status == StageStatus.COMPLETED,
            "pipeline_id": pipeline_result.pipeline_id,
            "execution_time": pipeline_result.total_execution_time,
            "stages_completed": len([r for r in pipeline_result.stage_results if r.status == StageStatus.COMPLETED]),
            "total_stages": len(pipeline_result.stage_results),
            "errors": pipeline_result.error_summary
        }

        # Add successful results
        if pipeline_result.product_description:
            response["product_description"] = pipeline_result.product_description.dict()

        if pipeline_result.generated_image:
            response["generated_image"] = pipeline_result.generated_image.dict()

        if pipeline_result.shopify_listing:
            response["shopify_listing"] = pipeline_result.shopify_listing.dict()

        return response

    async def get_health(self) -> Dict[str, Any]:
        """Get system health status."""
        return self.orchestrator.get_health_status()

    async def process_product_listing(self, product_description: str = None, product_input: 'ProductInput' = None, **kwargs) -> Any:
        """
        High-level method for processing product listings.
        Compatible with the web demo interface.
        """
        if product_input:
            return await self.orchestrator.execute_pipeline(product_input)
        elif product_description:
            # Create ProductInput from description
            from models.data_models import ProductInput
            product_input = ProductInput(product_description=product_description, **kwargs)
            return await self.orchestrator.execute_pipeline(product_input)
        else:
            raise ValueError("Either product_description or product_input must be provided")
