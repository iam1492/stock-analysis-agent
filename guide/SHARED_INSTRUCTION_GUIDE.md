# Shared Instruction System Guide

## Overview

The Stock Analysis Agent now supports dynamic shared instructions that can be updated in real-time through Firestore. This system allows all 12 agents to follow common guidelines while maintaining their specialized functionality.

## Architecture

### Components

1. **Firestore Configuration** (`app/sub_agents/utils/firestore_config.py`)
   - Loads shared instructions from `stock_agent_company/shared_instruction`
   - Provides fallback to default instruction if Firestore unavailable
   - Caches instructions in memory for O(1) lookups

2. **Instruction Templater** (`app/sub_agents/utils/instruction_templater.py`)
   - Combines shared instructions with agent-specific instructions
   - Supports template variable substitution with Session.state
   - Provides validation and error handling

3. **Agent Integration**
   - All 12 agents use `InstructionTemplater.create_agent_instruction()`
   - Shared instruction prepended to agent-specific instructions
   - Maintains backward compatibility with existing instruction structure

## Firestore Schema

### Collection: `stock_agent_company`

#### Document: `shared_instruction`

```json
{
  "instruction": "우리 회사는 세계 최고의 금융회사로 항상 고객에게 뛰어난 수익률을 가져다준다. 우리팀은 1년 이상의 장기 투자를 지향하는 투자를 하고 사실 위주로만 소통하며 높은 신뢰도를 가지는 리포트를 작성하는 것을 목표로 한다."
}
```

## Usage

### For Administrators

#### 1. Setting Shared Instructions

**Via Firebase Console:**
1. Open Firebase Console
2. Navigate to Firestore Database
3. Select `stock_agent_company` collection
4. Edit `shared_instruction` document
5. Update the `instruction` field

**Via Script:**
```python
from app.sub_agents.utils.firestore_config import FirestoreConfig

# Reload shared instruction
FirestoreConfig.reload_configs()
```

#### 2. Default Instruction

If Firestore is unavailable, the system falls back to:
```
우리 회사는 세계 최고의 금융회사로 항상 고객에게 뛰어난 수익률을 가져다준다. 우리팀은 1년 이상의 장기 투자를 지향하는 투자를 하고 사실 위주로만 소통하며 높은 신뢰도를 가지는 리포트를 작성하는 것을 목표로 한다.
```

### For Developers

#### 1. Creating New Agents

When creating new agents, use the instruction templater:

```python
from app.sub_agents.utils.instruction_templater import InstructionTemplater

def create_new_agent():
    # Base instruction template
    base_instruction = """
    [Agent-specific instructions here]
    """
    
    return LlmAgent(
        name="new_agent",
        model=lite_llm_model("new_agent"),
        description="Agent description",
        instruction=InstructionTemplater.create_agent_instruction(
            agent_name="new_agent",
            base_instruction=base_instruction
        ),
        # ... other parameters
    )
```

#### 2. Template Variables

The instruction templater supports these variables:

- **Session State Variables**: Automatically injected from `callback_context.state`
  - `{unique_id}`: Session unique identifier
  - `{timestamp}`: Session timestamp
  - `{user_id}`: User identifier
  - `{agent_results}`: Agent results tracking

- **Shared Instruction**: `{shared_instruction}` from Firestore

#### 3. Advanced Templating

For complex template scenarios:

```python
from app.sub_agents.utils.instruction_templater import InstructionTemplater

# Format with custom variables
formatted_instruction = InstructionTemplater.format_instruction(
    base_instruction="Custom {variable} instruction",
    session_state=session_state,
    additional_vars={"variable": "custom_value"}
)
```

## Agent List

All 12 agents have been updated to use shared instructions:

1. **Root Agent** (`app/agent.py`)
   - Coordinates entire workflow
   - Sets up session state

2. **Department Level** (Parallel execution)
   - **Stock Researcher**: Market research and news analysis
   - **Financial Team**: Balance sheet, income statement, cash flow, basic financial analysis
   - **Technical Analyst**: Technical indicators and trend analysis
   - **Quantitative Team**: Intrinsic value and growth analysis
   - **Macro Economy Analyst**: Economic indicators and market analysis

3. **Senior Advisors** (Sequential synthesis)
   - **Senior Financial Advisor**: Synthesizes financial team results
   - **Senior Quantitative Advisor**: Synthesizes quantitative team results

4. **Final Synthesis**
   - **Hedge Fund Manager**: Final investment recommendation

## Benefits

### 1. **Dynamic Configuration**
- Update instructions without code deployment
- Real-time changes across all agents
- A/B testing of instruction variations

### 2. **Consistency**
- All agents follow same company guidelines
- Unified tone and approach
- Consistent quality standards

### 3. **Maintainability**
- Single source of truth for instructions
- Easy to update and manage
- Version control through Firestore

### 4. **Fallback Safety**
- Graceful degradation if Firestore unavailable
- Default instructions ensure system continues working
- Error handling and logging

## Troubleshooting

### Common Issues

#### 1. Shared Instruction Not Loading
**Symptoms:**
- Agents using only base instructions
- Warning logs about missing shared instruction

**Solutions:**
1. Check Firestore connection:
   ```python
   from app.sub_agents.utils.firestore_config import FirestoreClient
   client = FirestoreClient.get_client()
   print(f"Client available: {client is not None}")
   ```

2. Verify document exists:
   - Collection: `stock_agent_company`
   - Document ID: `shared_instruction`
   - Field: `instruction`

3. Check permissions:
   - Firebase service account has Firestore read permissions
   - Environment variables set correctly

#### 2. Template Formatting Issues
**Symptoms:**
- Instructions not properly formatted
- Variables not replaced

**Solutions:**
1. Validate template syntax:
   ```python
   from app.sub_agents.utils.instruction_templater import InstructionTemplater
   valid = InstructionTemplater.validate_template(instruction)
   ```

2. Check variable names:
   - Use `{variable_name}` format
   - Ensure no unmatched braces

#### 3. Performance Issues
**Symptoms:**
- Slow instruction loading
- High memory usage

**Solutions:**
1. Enable caching (default enabled)
2. Monitor Firestore usage
3. Use connection pooling

## Monitoring

### Logging

The system provides comprehensive logging:

```python
import logging
logger = logging.getLogger(__name__)

# Debug level shows template processing
logger.debug("Template processing details")

# Info level shows successful operations
logger.info("Shared instruction loaded successfully")

# Warning level shows fallbacks and issues
logger.warning("Using default instruction - Firestore unavailable")

# Error level shows failures
logger.error("Failed to load shared instruction")
```

### Metrics

Monitor these key metrics:

1. **Instruction Load Time**: Time to load from Firestore
2. **Cache Hit Rate**: Percentage of instructions served from cache
3. **Fallback Rate**: How often default instructions are used
4. **Error Rate**: Failed instruction loads per hour

## Best Practices

### 1. Instruction Design
- Keep instructions concise and clear
- Use consistent formatting across agents
- Include specific examples and expected outputs
- Test instructions with various scenarios

### 2. Firestore Management
- Use document versioning for changes
- Implement approval workflow for updates
- Monitor Firestore usage and costs
- Set up alerts for document changes

### 3. Error Handling
- Always provide meaningful fallbacks
- Log all failures with context
- Implement retry logic for transient issues
- Monitor system health continuously

### 4. Performance Optimization
- Cache instructions in memory
- Minimize Firestore queries
- Use connection pooling
- Implement lazy loading where possible

## Security Considerations

### 1. Access Control
- Restrict Firestore write access to authorized users
- Use service accounts with minimal permissions
- Implement audit logging for instruction changes

### 2. Data Validation
- Validate instruction content before saving
- Sanitize user inputs in templates
- Prevent injection attacks through template variables

### 3. Compliance
- Ensure instructions comply with regulations
- Document all instruction changes
- Implement retention policies for old versions

## Future Enhancements

### Planned Features

1. **Instruction Versioning**
- Track instruction versions over time
- Rollback capability for problematic changes
- A/B testing framework

2. **Advanced Templating**
- Conditional logic in templates
- Loop constructs for repetitive patterns
- Custom function support

3. **Analytics Dashboard**
- Instruction performance metrics
- Agent behavior analysis
- User satisfaction tracking

4. **Multi-language Support**
- Language-specific instructions
- Localization framework
- Cultural adaptation capabilities

## Migration Guide

### From Static Instructions

1. **Backup Current Configuration**
   ```bash
   cp -r app/sub_agents/ backup/agents_before_shared_instructions
   ```

2. **Update Agent Files**
   - All agents already updated in this implementation
   - Verify imports include `InstructionTemplater`

3. **Configure Firestore**
   - Create `stock_agent_company` collection
   - Add `shared_instruction` document
   - Set initial instruction content

4. **Test System**
   - Verify all agents load shared instruction
   - Test fallback behavior
   - Monitor performance

### Rollback Procedure

If issues occur:

1. **Disable Shared Instructions**
   ```python
   # Temporarily disable shared instruction loading
   FirestoreConfig._shared_instruction_cache = None
   ```

2. **Restore Static Instructions**
   - Revert agent files to backup
   - Remove `InstructionTemplater` imports
   - Test system functionality

## Support

For issues or questions about the shared instruction system:

1. **Documentation**: Check this guide and code comments
2. **Logs**: Review application logs for error details
3. **Monitoring**: Check Firestore connection and performance
4. **Testing**: Use development environment for validation

## Conclusion

The shared instruction system provides a powerful, flexible way to manage agent behavior dynamically. By following this guide, administrators can easily update agent instructions while developers can maintain robust, error-resistant implementations.

The system balances flexibility with reliability, ensuring that agents can adapt to new requirements while maintaining consistent operation even when external dependencies fail.