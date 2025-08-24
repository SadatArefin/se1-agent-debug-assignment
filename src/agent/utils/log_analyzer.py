"""Log analysis utilities for the agent system."""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter


class LogAnalyzer:
    """Analyze and summarize agent log files."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        if not self.log_dir.exists():
            raise ValueError(f"Log directory {log_dir} does not exist")
    
    def get_latest_log_files(self) -> Dict[str, Path]:
        """Get the most recent log files."""
        today = datetime.now().strftime('%Y%m%d')
        
        log_files = {
            'agent': self.log_dir / f"agent_{today}.log",
            'performance': self.log_dir / f"performance_{today}.log",
            'tools': self.log_dir / f"tools_{today}.log",
            'errors': self.log_dir / f"errors_{today}.log"
        }
        
        # Return only files that exist
        return {name: path for name, path in log_files.items() if path.exists()}
    
    def parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a structured log line."""
        try:
            # Find JSON part (after the last " - ")
            parts = line.split(" - ")
            if len(parts) < 4:
                return None
            
            timestamp_str = parts[0]
            logger_name = parts[1]
            level = parts[2]
            message = " - ".join(parts[3:])
            
            # Try to extract JSON from the message
            if ":" in message and ("{" in message or "[" in message):
                message_type, json_part = message.split(":", 1)
                try:
                    data = json.loads(json_part.strip())
                    return {
                        "timestamp": timestamp_str,
                        "logger": logger_name,
                        "level": level,
                        "message_type": message_type.strip(),
                        "data": data
                    }
                except json.JSONDecodeError:
                    pass
            
            return {
                "timestamp": timestamp_str,
                "logger": logger_name,
                "level": level,
                "message": message,
                "data": {}
            }
        except Exception:
            return None
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance metrics from logs."""
        log_files = self.get_latest_log_files()
        perf_file = log_files.get('performance')
        
        if not perf_file or not perf_file.exists():
            return {"error": "No performance log file found"}
        
        latencies = []
        success_count = 0
        error_count = 0
        query_lengths = []
        response_lengths = []
        
        with open(perf_file, 'r') as f:
            for line in f:
                parsed = self.parse_log_line(line)
                if parsed and parsed.get("message_type") == "PERFORMANCE":
                    data = parsed["data"]
                    latencies.append(data.get("latency_ms", 0))
                    
                    if data.get("success"):
                        success_count += 1
                    else:
                        error_count += 1
                    
                    query_lengths.append(data.get("query_length", 0))
                    response_lengths.append(data.get("response_length", 0))
        
        if not latencies:
            return {"error": "No performance data found"}
        
        return {
            "total_requests": len(latencies),
            "success_rate": success_count / len(latencies) * 100,
            "latency_stats": {
                "min_ms": min(latencies),
                "max_ms": max(latencies),
                "avg_ms": sum(latencies) / len(latencies),
                "median_ms": sorted(latencies)[len(latencies) // 2]
            },
            "query_stats": {
                "avg_length": sum(query_lengths) / len(query_lengths) if query_lengths else 0,
                "max_length": max(query_lengths) if query_lengths else 0
            },
            "response_stats": {
                "avg_length": sum(response_lengths) / len(response_lengths) if response_lengths else 0,
                "max_length": max(response_lengths) if response_lengths else 0
            }
        }
    
    def analyze_tool_usage(self) -> Dict[str, Any]:
        """Analyze tool usage patterns."""
        log_files = self.get_latest_log_files()
        tools_file = log_files.get('tools')
        
        if not tools_file or not tools_file.exists():
            return {"error": "No tools log file found"}
        
        tool_usage = Counter()
        tool_success = defaultdict(int)
        tool_errors = defaultdict(int)
        tool_latencies = defaultdict(list)
        
        with open(tools_file, 'r') as f:
            for line in f:
                parsed = self.parse_log_line(line)
                if parsed and parsed.get("message_type") == "TOOL_EXECUTION":
                    data = parsed["data"]
                    tool_name = data.get("tool_name", "unknown")
                    
                    tool_usage[tool_name] += 1
                    
                    if data.get("success"):
                        tool_success[tool_name] += 1
                    else:
                        tool_errors[tool_name] += 1
                    
                    latency = data.get("latency_ms", 0)
                    tool_latencies[tool_name].append(latency)
        
        # Calculate stats for each tool
        tool_stats = {}
        for tool_name in tool_usage:
            latencies = tool_latencies[tool_name]
            tool_stats[tool_name] = {
                "usage_count": tool_usage[tool_name],
                "success_count": tool_success[tool_name],
                "error_count": tool_errors[tool_name],
                "success_rate": (tool_success[tool_name] / tool_usage[tool_name]) * 100,
                "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0
            }
        
        return {
            "total_tool_executions": sum(tool_usage.values()),
            "unique_tools_used": len(tool_usage),
            "most_used_tools": tool_usage.most_common(5),
            "tool_details": tool_stats
        }
    
    def analyze_errors(self) -> Dict[str, Any]:
        """Analyze error patterns."""
        log_files = self.get_latest_log_files()
        errors_file = log_files.get('errors')
        
        if not errors_file or not errors_file.exists():
            return {"error": "No errors log file found"}
        
        error_types = Counter()
        error_messages = Counter()
        errors_by_hour = defaultdict(int)
        
        with open(errors_file, 'r') as f:
            for line in f:
                parsed = self.parse_log_line(line)
                if parsed:
                    data = parsed.get("data", {})
                    
                    if "error_type" in data:
                        error_types[data["error_type"]] += 1
                    
                    if "error_message" in data:
                        # Truncate long error messages
                        msg = data["error_message"][:100]
                        error_messages[msg] += 1
                    
                    # Extract hour from timestamp
                    try:
                        timestamp = parsed["timestamp"]
                        hour = timestamp.split()[1].split(":")[0]
                        errors_by_hour[hour] += 1
                    except:
                        pass
        
        return {
            "total_errors": sum(error_types.values()),
            "error_types": dict(error_types.most_common()),
            "common_errors": dict(error_messages.most_common(5)),
            "errors_by_hour": dict(errors_by_hour)
        }
    
    def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent request details."""
        log_files = self.get_latest_log_files()
        agent_file = log_files.get('agent')
        
        if not agent_file or not agent_file.exists():
            return []
        
        requests = []
        
        with open(agent_file, 'r') as f:
            for line in f:
                parsed = self.parse_log_line(line)
                if parsed and parsed.get("message_type") in ["REQUEST_START", "REQUEST_END"]:
                    data = parsed["data"]
                    if parsed["message_type"] == "REQUEST_START":
                        requests.append({
                            "request_id": data.get("request_id"),
                            "timestamp": data.get("timestamp"),
                            "query": data.get("query", "")[:100],
                            "status": "started"
                        })
                    elif parsed["message_type"] == "REQUEST_END":
                        # Find matching start request and update it
                        request_id = data.get("request_id")
                        for req in reversed(requests):
                            if req.get("request_id") == request_id:
                                req.update({
                                    "status": "completed" if data.get("success") else "failed",
                                    "latency_ms": data.get("latency_ms"),
                                    "response": data.get("response", "")[:100]
                                })
                                break
        
        return list(reversed(requests[-limit:]))
    
    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report."""
        report = ["=== Agent Log Analysis Report ===\n"]
        
        # Performance analysis
        perf_analysis = self.analyze_performance()
        if "error" not in perf_analysis:
            report.append("📊 PERFORMANCE METRICS")
            report.append(f"Total Requests: {perf_analysis['total_requests']}")
            report.append(f"Success Rate: {perf_analysis['success_rate']:.1f}%")
            report.append(f"Average Latency: {perf_analysis['latency_stats']['avg_ms']:.1f}ms")
            report.append(f"Latency Range: {perf_analysis['latency_stats']['min_ms']:.1f}ms - {perf_analysis['latency_stats']['max_ms']:.1f}ms")
            report.append("")
        
        # Tool usage analysis
        tool_analysis = self.analyze_tool_usage()
        if "error" not in tool_analysis:
            report.append("🔧 TOOL USAGE")
            report.append(f"Total Tool Executions: {tool_analysis['total_tool_executions']}")
            report.append(f"Unique Tools Used: {tool_analysis['unique_tools_used']}")
            report.append("Most Used Tools:")
            for tool, count in tool_analysis['most_used_tools']:
                success_rate = tool_analysis['tool_details'][tool]['success_rate']
                avg_latency = tool_analysis['tool_details'][tool]['avg_latency_ms']
                report.append(f"  • {tool}: {count} uses, {success_rate:.1f}% success, {avg_latency:.1f}ms avg")
            report.append("")
        
        # Error analysis
        error_analysis = self.analyze_errors()
        if "error" not in error_analysis and error_analysis['total_errors'] > 0:
            report.append("❌ ERROR ANALYSIS")
            report.append(f"Total Errors: {error_analysis['total_errors']}")
            report.append("Error Types:")
            for error_type, count in list(error_analysis['error_types'].items())[:5]:
                report.append(f"  • {error_type}: {count}")
            report.append("")
        
        # Recent requests
        recent = self.get_recent_requests(5)
        if recent:
            report.append("📝 RECENT REQUESTS")
            for req in recent:
                status_emoji = "✅" if req['status'] == "completed" else "❌" if req['status'] == "failed" else "⏳"
                latency = f" ({req.get('latency_ms', 0):.1f}ms)" if req.get('latency_ms') else ""
                report.append(f"  {status_emoji} {req['query']}{latency}")
            report.append("")
        
        report.append(f"Log directory: {self.log_dir}")
        
        return "\n".join(report)


def analyze_logs(log_dir: str = "logs") -> str:
    """Quick function to analyze logs and return a summary."""
    try:
        analyzer = LogAnalyzer(log_dir)
        return analyzer.generate_summary_report()
    except Exception as e:
        return f"Error analyzing logs: {e}"


if __name__ == "__main__":
    print(analyze_logs())
