"""Tests for policies functionality."""
import pytest
import time
from unittest.mock import Mock
from agent.core.policies import PolicyManager, RetryPolicy, ExecutionPolicy


class TestRetryPolicy:
    """Test retry policy functionality."""
    
    def test_get_delay_exponential(self):
        """Test exponential backoff delay calculation."""
        policy = RetryPolicy(base_delay=1.0, exponential_base=2.0, max_delay=10.0)
        
        assert policy.get_delay(1) == 1.0
        assert policy.get_delay(2) == 2.0
        assert policy.get_delay(3) == 4.0
        assert policy.get_delay(4) == 8.0
        assert policy.get_delay(5) == 10.0  # Capped at max_delay


class TestPolicyManager:
    """Test policy manager functionality."""
    
    def test_with_retry_success_first_attempt(self):
        """Test successful operation on first attempt."""
        policy_manager = PolicyManager()
        
        def successful_operation():
            return "success"
        
        result = policy_manager.with_retry(successful_operation)
        assert result == "success"
    
    def test_with_retry_success_after_failure(self):
        """Test successful operation after initial failures."""
        policy_manager = PolicyManager(RetryPolicy(max_attempts=3, base_delay=0.01))
        
        call_count = 0
        def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = policy_manager.with_retry(flaky_operation)
        assert result == "success"
        assert call_count == 3
    
    def test_with_retry_final_failure(self):
        """Test operation that fails all attempts."""
        policy_manager = PolicyManager(RetryPolicy(max_attempts=2, base_delay=0.01))
        
        def failing_operation():
            raise Exception("Persistent failure")
        
        with pytest.raises(Exception, match="Operation failed after 2 attempts"):
            policy_manager.with_retry(failing_operation)
    
    def test_with_retry_context(self):
        """Test retry with context information."""
        policy_manager = PolicyManager(RetryPolicy(max_attempts=1, base_delay=0.01))
        
        def failing_operation():
            raise Exception("Failure")
        
        with pytest.raises(Exception, match="context: test operation"):
            policy_manager.with_retry(failing_operation, context="test operation")
    
    def test_check_step_limit_within_limit(self):
        """Test step limit checking within limit."""
        policy_manager = PolicyManager(execution_policy=ExecutionPolicy(max_steps=5))
        
        assert policy_manager.check_step_limit(1) is True
        assert policy_manager.check_step_limit(5) is True
    
    def test_check_step_limit_exceeds_limit(self):
        """Test step limit checking when exceeded."""
        policy_manager = PolicyManager(execution_policy=ExecutionPolicy(max_steps=5))
        
        assert policy_manager.check_step_limit(6) is False
        assert policy_manager.check_step_limit(10) is False
    
    def test_check_time_limit_within_limit(self):
        """Test time limit checking within limit."""
        policy_manager = PolicyManager(execution_policy=ExecutionPolicy(max_execution_time=1.0))
        
        start_time = time.time()
        assert policy_manager.check_time_limit(start_time) is True
    
    def test_check_time_limit_exceeds_limit(self):
        """Test time limit checking when exceeded."""
        policy_manager = PolicyManager(execution_policy=ExecutionPolicy(max_execution_time=0.1))
        
        start_time = time.time() - 1.0  # Simulate 1 second ago
        assert policy_manager.check_time_limit(start_time) is False
