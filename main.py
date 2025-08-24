import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your question here\"")
        print("       python main.py --log-summary  # Show logging information")
        print("       python main.py --analyze-logs # Analyze log files")
        print("       python main.py --verbose \"query\" # Enable verbose console logging")
        sys.exit(1)
    
    # Check for verbose flag FIRST, before any imports
    verbose_mode = False
    args = sys.argv[1:]
    if "--verbose" in args:
        verbose_mode = True
        args.remove("--verbose")
        if not args:
            print("Please provide a query after --verbose flag")
            sys.exit(1)
    
    # Set environment variables BEFORE importing agent modules
    if "LOG_LEVEL" not in os.environ:
        os.environ["LOG_LEVEL"] = "INFO"
    if "ENABLE_CONSOLE_LOGGING" not in os.environ:
        os.environ["ENABLE_CONSOLE_LOGGING"] = "true" if verbose_mode else "false"
    if "ENABLE_TELEMETRY" not in os.environ:
        os.environ["ENABLE_TELEMETRY"] = "true"
    
    # NOW import agent modules (after environment is set)
    from agent.agent import answer, get_log_summary
    
    # Handle special commands
    if args and args[0] == "--log-summary":
        summary = get_log_summary()
        print("=== Agent Logging Summary ===")
        print(f"Session ID: {summary['session_id']}")
        print(f"Total requests: {summary['total_requests']}")
        print(f"Log directory: {summary['log_directory']}")
        print("\nLog files:")
        for log_type, path in summary['log_files'].items():
            print(f"  {log_type}: {path}")
        return
    
    if args and args[0] == "--analyze-logs":
        try:
            from src.agent.utils.log_analyzer import analyze_logs
            analysis = analyze_logs()
            print(analysis)
        except ImportError:
            print("Log analyzer not available")
        except Exception as e:
            print(f"Error analyzing logs: {e}")
        return
    
    # Process the query
    q = " ".join(args)
    
    if not verbose_mode:
        print(f"Processing query: {q}")
        print("=" * 50)
    else:
        print(f"Processing query (verbose mode): {q}")
        print("=" * 50)
    
    try:
        out = answer(q)
        print(out)
        
        # Show minimal log info after processing (only if not verbose)
        if not verbose_mode:
            summary = get_log_summary()
            print(f"\n✓ Request #{summary['total_requests']} completed • Logs: {summary['log_directory']}")
        else:
            # Show detailed log summary in verbose mode
            summary = get_log_summary()
            print("\n" + "=" * 50)
            print(f"Logs saved to: {summary['log_directory']}")
            print(f"Request #{summary['total_requests']} completed")
            print("Run 'python main.py --analyze-logs' for detailed analysis")
        
    except Exception as e:
        print(f"Error processing query: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
