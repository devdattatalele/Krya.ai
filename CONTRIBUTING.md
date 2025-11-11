# Contributing to Krya.ai

Thank you for your interest in contributing to Krya.ai! This document provides guidelines and instructions for contributing.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, intimidation, or discrimination
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.8 or higher
- Node.js 16+ and npm
- Rust and Cargo (for Tauri development)
- Git
- A Google Gemini API key (for testing)

### Find an Issue to Work On

1. Check the [GitHub Issues](https://github.com/devdattatalele/Krya.ai/issues)
2. Look for issues labeled `good first issue` or `help wanted`
3. Comment on the issue to express your interest
4. Wait for maintainer approval before starting work

### Creating New Issues

Before creating a new issue:

1. Search existing issues to avoid duplicates
2. Use issue templates when available
3. Provide clear, detailed descriptions
4. Include steps to reproduce (for bugs)
5. Include expected vs actual behavior

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/Krya.ai.git
cd Krya.ai
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r src/requirements.txt
```

### 3. Set Up Configuration

```bash
# Copy example configuration
cp .env.example .env
cp config.json.example config.json

# Edit .env and add your API key
# GOOGLE_API_KEY=your_key_here
```

### 4. Set Up UI (Optional)

```bash
cd ui
npm install
cd ..
```

### 5. Verify Setup

```bash
# Run the backend
cd src
python run_server.py

# In another terminal, test the API
curl http://localhost:8000
```

## Making Changes

### Branch Naming Convention

Create a feature branch with a descriptive name:

```bash
git checkout -b feature/short-description
git checkout -b fix/bug-description
git checkout -b docs/documentation-update
```

Examples:
- `feature/add-code-validation`
- `fix/memory-leak-in-executor`
- `docs/update-installation-guide`

### Commit Message Guidelines

Write clear, meaningful commit messages:

```
<type>: <short summary> (max 50 chars)

<detailed description if needed>
<explain why, not what>

Fixes #123
```

Types:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: Add input validation for user prompts

Validates prompt length and content before processing
to prevent API errors and improve user experience.

Fixes #42
```

```
fix: Prevent memory leak in execution loop

Properly clean up processes after execution to
prevent memory from growing unbounded.

Closes #78
```

## Submitting Changes

### Before Submitting

- [ ] Test your changes thoroughly
- [ ] Run linters and formatters
- [ ] Update documentation if needed
- [ ] Add tests for new functionality
- [ ] Ensure all existing tests pass
- [ ] Update CHANGELOG.md (if applicable)

### Pull Request Process

1. **Push your changes:**
   ```bash
   git push origin feature/your-branch-name
   ```

2. **Create Pull Request on GitHub:**
   - Use a clear, descriptive title
   - Reference related issues (e.g., "Fixes #123")
   - Describe what changed and why
   - Include screenshots for UI changes
   - List any breaking changes

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Related Issues
   Fixes #123
   
   ## Testing
   How did you test these changes?
   
   ## Screenshots (if applicable)
   
   ## Checklist
   - [ ] My code follows the project's style guidelines
   - [ ] I have tested my changes
   - [ ] I have updated documentation
   - [ ] I have added tests
   ```

4. **Respond to feedback:**
   - Be open to suggestions
   - Make requested changes promptly
   - Ask questions if unclear
   - Update your PR as needed

## Coding Standards

### Python Style Guide

Follow PEP 8 guidelines:

```python
# Use 4 spaces for indentation
def example_function(param1: str, param2: int) -> bool:
    """
    Docstring describing the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
    # Use meaningful variable names
    result = process_data(param1)
    return result is not None
```

### Type Hints

Use type hints for function parameters and returns:

```python
from typing import Optional, List, Dict

def get_config(key: str) -> Optional[Dict[str, Any]]:
    """Get configuration by key."""
    pass
```

### Code Organization

```
src/
├── functions/      # Core functionality
├── config/        # Configuration
├── system/        # System utilities
└── UI/           # User interface
```

### Error Handling

Always handle errors appropriately:

```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise
finally:
    cleanup_resources()
```

### Logging

Use proper logging instead of print:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Starting process")
logger.warning("Something unexpected happened")
logger.error("An error occurred", exc_info=True)
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_example.py
```

### Writing Tests

```python
import pytest
from functions.gen import generate_code

def test_generate_code_basic():
    """Test basic code generation."""
    prompt = "Print hello world"
    code = generate_code(prompt)
    
    assert code is not None
    assert "print" in code.lower()
    assert "hello" in code.lower()

def test_generate_code_error_handling():
    """Test error handling in code generation."""
    with pytest.raises(ValueError):
        generate_code("")  # Empty prompt should raise error
```

### Test Coverage

- Aim for at least 80% code coverage
- Test edge cases and error conditions
- Mock external dependencies (API calls)
- Test both success and failure paths

## Documentation

### Code Documentation

Document all public functions and classes:

```python
def process_prompt(prompt: str, max_retries: int = 3) -> tuple[str, str]:
    """
    Process a user prompt and generate executable code.
    
    This function generates Python code based on natural language
    input and executes it with retry logic for error handling.
    
    Args:
        prompt: Natural language description of desired automation
        max_retries: Maximum number of retry attempts on failure
        
    Returns:
        A tuple of (generated_code, execution_status)
        
    Raises:
        ValueError: If prompt is empty or invalid
        APIError: If API call fails after all retries
        
    Example:
        >>> code, status = process_prompt("Open calculator")
        >>> print(status)
        "Execution completed successfully"
    """
    pass
```

### README Updates

Update README.md when:
- Adding new features
- Changing installation steps
- Modifying configuration options
- Adding new dependencies

### Changelog

Keep CHANGELOG.md updated with notable changes:

```markdown
## [Unreleased]
### Added
- New feature X

### Changed
- Modified behavior of Y

### Fixed
- Bug fix for Z
```

## Review Process

### What Reviewers Look For

- Code quality and style
- Test coverage
- Documentation completeness
- Performance implications
- Security considerations
- Breaking changes

### Response Times

- Initial review: Within 3-5 business days
- Follow-up reviews: Within 1-2 business days
- Be patient, maintainers are volunteers

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributor graph

## Questions?

- Open a discussion on GitHub
- Comment on existing issues
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Krya.ai! 🎉
