# Contributing to Agent Web

Thank you for your interest in contributing to Agent Web! This project aims to create a decentralized protocol for AI agent collaboration, and we welcome contributions from the community.

## 🎯 Ways to Contribute

### 1. Report Bugs
If you find a bug, please create an issue on GitHub with:
- **Clear title** describing the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs. actual behavior
- **Environment details** (OS, Python version, etc.)
- **Error messages** or logs if applicable

### 2. Suggest Features
Have an idea for improving Agent Web? Open an issue with:
- **Use case** explaining why this feature is needed
- **Proposed solution** with implementation ideas
- **Alternatives considered** if applicable
- **Impact assessment** on existing functionality

### 3. Improve Documentation
Documentation improvements are always welcome:
- Fix typos or clarify confusing sections
- Add code examples or tutorials
- Translate documentation to other languages
- Create video tutorials or blog posts

### 4. Submit Code Changes
We accept pull requests for bug fixes and new features!

## 🚀 Getting Started

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/agent-web.git
   cd agent-web
   ```

3. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Running Tests

```bash
# Run all tests (coming soon)
pytest

# Run specific test file
pytest tests/test_agent.py

# Run with coverage
pytest --cov=agent_web
```

### Code Style

We follow PEP 8 style guidelines for Python code:

```bash
# Check code style
flake8 agent_web.py

# Format code automatically
black agent_web.py

# Type checking
mypy agent_web.py
```

## 📝 Pull Request Process

### Before Submitting

1. **Test your changes** thoroughly
2. **Update documentation** if you're changing APIs or adding features
3. **Follow code style** guidelines
4. **Write clear commit messages** explaining your changes
5. **Squash commits** if you have many small commits

### Commit Message Format

Use clear, descriptive commit messages:

```
feat: Add support for batch agent registration

- Implement batch_register() method in Agent class
- Add validation for batch registration requests
- Update documentation with batch registration examples

Fixes #123
```

**Commit types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, no logic change)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks (dependencies, build, etc.)

### Submitting the PR

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub with:
   - **Clear title** summarizing the change
   - **Description** explaining what and why
   - **Related issues** (e.g., "Fixes #123")
   - **Testing details** showing how you verified the changes
   - **Screenshots** if applicable (UI changes)

3. **Respond to review feedback** promptly
4. **Update your PR** based on reviewer suggestions
5. **Squash and merge** once approved

## 🔍 Code Review Guidelines

### For Contributors

- Be open to feedback and suggestions
- Explain your reasoning for implementation choices
- Ask questions if feedback is unclear
- Be patient during the review process

### For Reviewers

- Be respectful and constructive
- Explain the reasoning behind suggestions
- Approve PRs that improve the codebase
- Focus on significant issues, not nitpicks

## 🏗️ Architecture Guidelines

### Adding New Features

When adding new features to Agent Web:

1. **Maintain backward compatibility** when possible
2. **Follow existing patterns** in the codebase
3. **Keep dependencies minimal** - avoid adding unnecessary libraries
4. **Consider security implications** - all agent communication must remain secure
5. **Document new APIs** in code and in `API.md`

### Core Principles

- **Decentralization**: Avoid central points of control
- **Security**: All messages must be cryptographically signed
- **Interoperability**: Work across different AI frameworks and languages
- **Simplicity**: Keep the protocol simple and understandable
- **Reliability**: Ensure high availability through hybrid discovery

## 📚 Project Structure

```
agent-web/
├── agent_web.py           # Core SDK implementation
├── registry_server.py     # Central cache for hybrid discovery
├── examples/              # Example agents and demos
│   ├── travel_agent.py
│   ├── airline_agent.py
│   ├── restaurant_agent.py
│   └── unified_assistant.py
├── tests/                 # Test suite
├── docs/                  # Additional documentation
├── README.md              # Project overview
├── CONTRIBUTING.md        # This file
├── LICENSE                # MIT License
└── requirements.txt       # Python dependencies
```

## 🐛 Reporting Security Issues

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, email security@agentweb.org with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We'll respond within 48 hours and work with you to address the issue.

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Race or ethnicity
- Age
- Religion or belief system

### Our Standards

**Positive behaviors:**
- Being respectful and considerate
- Accepting constructive criticism gracefully
- Focusing on what's best for the community
- Showing empathy toward others

**Unacceptable behaviors:**
- Harassment or discriminatory language
- Personal attacks or insults
- Publishing others' private information
- Trolling or deliberately disruptive behavior

### Enforcement

Instances of unacceptable behavior may be reported to project maintainers. All complaints will be reviewed and investigated, resulting in a response deemed necessary and appropriate.

## 🎓 Learning Resources

### Understanding Agent Web

- Read the [README.md](README.md) for project overview
- Review [API.md](API.md) for SDK documentation
- Study example agents in `examples/` directory
- Check out the [architectural overview](docs/architecture.md)

### Distributed Systems Concepts

- **Kademlia DHT**: [Original paper](https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf)
- **Decentralized Identifiers**: [W3C DID spec](https://www.w3.org/TR/did-core/)
- **Public Key Infrastructure**: Understanding RSA and digital signatures

### Python Best Practices

- [PEP 8 Style Guide](https://pep8.org/)
- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [Type hints guide](https://docs.python.org/3/library/typing.html)

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Project website (coming soon)

Thank you for contributing to Agent Web! Together we're building the future of decentralized AI collaboration. 🚀

## 📞 Questions?

- **GitHub Discussions**: For general questions and brainstorming
- **GitHub Issues**: For bug reports and feature requests
- **Discord**: Join our community (link coming soon)
- **Email**: contribute@agentweb.org

---

*Last updated: 2024-10-19*
