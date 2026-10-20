# Contributing to Python Remote Debug Skill

Thank you for your interest in contributing to this Claude Code skill!

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub with:

- A clear description of the problem or feature
- Steps to reproduce (for bugs)
- Your Python version and operating system
- Any relevant error messages or output

### Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-improvement`)
3. Make your changes
4. Test your changes locally:
   ```bash
   claude --plugin-dir .
   ```
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/my-improvement`)
7. Open a Pull Request

### Code Style

- Keep debug scripts simple and self-contained
- Add docstrings explaining what scripts do
- Test with both regular Python processes and gevent workers
- Update SKILL.md if adding new capabilities

### Testing

Before submitting:

1. Test the skill loads correctly:
   ```bash
   claude --plugin-dir .
   # Then run: /python-remote-debug:debug-remote
   ```

2. Test debug scripts work on a sample process:
   ```bash
   # Start a test Python process
   python3.14 -c "import time; time.sleep(60)" &
   PID=$!

   # Test thread debugging
   sudo python3.14 -c "import sys; sys.remote_exec($PID, 'skills/debug-remote/scripts/debug_threads.py')"
   cat /tmp/debug_threads_$PID.txt

   # Clean up
   kill $PID
   ```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
