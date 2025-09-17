"""
Base agent architecture for the Multi-Agent Product Listing System.

This module defines abstract base classes and interfaces for all agents in the system,
providing a consistent structure for agent implementation and communication.
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type
from datetime import datetime

from ..models.data_models import (
    AgentResult, AgentType, StageStatus, AgentConfig
)

class AgentException(Exception):
    """Base exception class for agent-related errors."""

    def __init__(self, message: str, agent_type: AgentType, retry_count: int = 0):
        super().__init__(message)
        self.agent_type = agent_type
        self.retry_count = retry_count
        self.timestamp = datetime.now()

class AgentTimeoutException(AgentException):
    """Exception raised when an agent operation times out."""
    pass

class AgentValidationException(AgentException):
    """Exception raised when agent input/output validation fails."""
    pass

class AgentConfigurationException(AgentException):
    """Exception raised when agent configuration is invalid."""
    pass

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    Provides common functionality for:
    - Configuration management
    - Error handling and retries
    - Logging
    - Execution timing
    - Result standardization
    """

    def __init__(self, config: AgentConfig, logger: Optional[logging.Logger] = None):
        """
        Initialize the base agent.

        Args:
            config: Agent configuration settings
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger(f"{self.__class__.__name__}")
        self.agent_type = config.agent_type
        self.stage = self._get_stage_number()

        # Validate configuration
        self._validate_config()

        # Initialize agent-specific settings
        self._initialize()

    @abstractmethod
    def _get_stage_number(self) -> int:
        """Return the stage number for this agent."""
        pass

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize agent-specific settings and resources."""
        pass

    @abstractmethod
    async def _execute_core(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core execution logic for the agent.

        Args:
            input_data: Input data for processing

        Returns:
            Dict containing the agent's output data

        Raises:
            AgentException: If execution fails
        """
        pass

    @abstractmethod
    def _validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data for the agent.

        Args:
            input_data: Input data to validate

        Returns:
            True if valid, False otherwise

        Raises:
            AgentValidationException: If validation fails
        """
        pass

    @abstractmethod
    def _validate_output(self, output_data: Dict[str, Any]) -> bool:
        """
        Validate output data from the agent.

        Args:
            output_data: Output data to validate

        Returns:
            True if valid, False otherwise

        Raises:
            AgentValidationException: If validation fails
        """
        pass

    def _validate_config(self) -> None:
        """
        Validate agent configuration.

        Raises:
            AgentConfigurationException: If configuration is invalid
        """
        if not self.config.enabled:
            self.logger.warning(f"Agent {self.agent_type} is disabled")

        if self.config.max_retries < 0:
            raise AgentConfigurationException(
                "max_retries cannot be negative", 
                self.agent_type
            )

        if self.config.timeout < 30:
            raise AgentConfigurationException(
                "timeout must be at least 30 seconds", 
                self.agent_type
            )

    async def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Execute the agent with proper error handling and retries.

        Args:
            input_data: Input data for processing

        Returns:
            AgentResult containing execution results and metadata
        """
        if not self.config.enabled:
            return AgentResult(
                agent_type=self.agent_type,
                stage=self.stage,
                status=StageStatus.SKIPPED,
                data={},
                error_message="Agent is disabled"
            )

        start_time = time.time()
        retry_count = 0
        last_exception = None

        self.logger.info(f"Starting execution for {self.agent_type} (Stage {self.stage})")

        while retry_count <= self.config.max_retries:
            try:
                # Validate input
                if not self._validate_input(input_data):
                    raise AgentValidationException(
                        "Input validation failed", 
                        self.agent_type, 
                        retry_count
                    )

                # Execute with timeout
                output_data = await asyncio.wait_for(
                    self._execute_core(input_data),
                    timeout=self.config.timeout
                )

                # Validate output
                if not self._validate_output(output_data):
                    raise AgentValidationException(
                        "Output validation failed", 
                        self.agent_type, 
                        retry_count
                    )

                execution_time = time.time() - start_time

                self.logger.info(
                    f"Successfully completed {self.agent_type} in {execution_time:.2f}s"
                )

                return AgentResult(
                    agent_type=self.agent_type,
                    stage=self.stage,
                    status=StageStatus.COMPLETED,
                    data=output_data,
                    execution_time=execution_time,
                    retry_count=retry_count,
                    metadata={"input_size": len(str(input_data))}
                )

            except asyncio.TimeoutError:
                last_exception = AgentTimeoutException(
                    f"Agent execution timed out after {self.config.timeout}s",
                    self.agent_type,
                    retry_count
                )

            except AgentException as e:
                last_exception = e

            except Exception as e:
                last_exception = AgentException(
                    f"Unexpected error: {str(e)}",
                    self.agent_type,
                    retry_count
                )

            retry_count += 1

            if retry_count <= self.config.max_retries:
                wait_time = min(2 ** retry_count, 30)  # Exponential backoff, max 30s
                self.logger.warning(
                    f"Retry {retry_count}/{self.config.max_retries} for {self.agent_type} "
                    f"after {wait_time}s due to: {str(last_exception)}"
                )
                await asyncio.sleep(wait_time)

        # All retries exhausted
        execution_time = time.time() - start_time

        self.logger.error(
            f"Failed to execute {self.agent_type} after {retry_count} attempts: "
            f"{str(last_exception)}"
        )

        return AgentResult(
            agent_type=self.agent_type,
            stage=self.stage,
            status=StageStatus.FAILED,
            data={},
            error_message=str(last_exception),
            execution_time=execution_time,
            retry_count=retry_count - 1
        )

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status information for the agent.

        Returns:
            Dict containing health status information
        """
        return {
            "agent_type": self.agent_type.value,
            "stage": self.stage,
            "enabled": self.config.enabled,
            "max_retries": self.config.max_retries,
            "timeout": self.config.timeout,
            "config_valid": True,  # If we got here, config is valid
            "timestamp": datetime.now().isoformat()
        }

class AgentFactory:
    """Factory class for creating agent instances."""

    _agent_registry: Dict[AgentType, Type[BaseAgent]] = {}

    @classmethod
    def register_agent(cls, agent_type: AgentType, agent_class: Type[BaseAgent]):
        """
        Register an agent class for creation.

        Args:
            agent_type: Type of agent to register
            agent_class: Agent class to register
        """
        cls._agent_registry[agent_type] = agent_class

    @classmethod
    def create_agent(
        cls, 
        agent_type: AgentType, 
        config: AgentConfig, 
        logger: Optional[logging.Logger] = None
    ) -> BaseAgent:
        """
        Create an agent instance.

        Args:
            agent_type: Type of agent to create
            config: Agent configuration
            logger: Optional logger instance

        Returns:
            Agent instance

        Raises:
            AgentConfigurationException: If agent type is not registered
        """
        if agent_type not in cls._agent_registry:
            raise AgentConfigurationException(
                f"Agent type {agent_type} is not registered",
                agent_type
            )

        agent_class = cls._agent_registry[agent_type]
        return agent_class(config, logger)

    @classmethod
    def get_registered_agents(cls) -> Dict[AgentType, Type[BaseAgent]]:
        """Get all registered agent types."""
        return cls._agent_registry.copy()
