import os
import json
try:
    from analysis.sigma_load import load_sigma_rules
    from analysis.sigma_match import check_if_event_matches_rule
except ImportError:
    from sigma_load import load_sigma_rules
    from sigma_match import check_if_event_matches_rule

def run_sigma_pipeline(log_events, rules_folder):
    rules = load_sigma_rules(rules_folder)
    matches = []
    matched_rule_ids = set()
    
    for event in log_events:
        for rule in rules:
            if check_if_event_matches_rule(event, rule):
                rule_id = rule.get('id', 'unknown')
                matched_rule_ids.add(rule_id)
                
                match_data = {
                    "rule_id": rule_id,
                    "rule_title": rule.get('title', 'Unnamed Rule'),
                    "severity": rule.get('level', 'unknown'),
                    "computer": event.get('computer', 'Unknown'),
                    "event_id": event.get('event_id', 'N/A'),
                    "timestamp": event.get('timestamp', 'N/A'),
                    "event_data": event
                }
                matches.append(match_data)
                
                print(f"ALERT #{len(matches)}: Rule: {rule.get('title', 'Unnamed Rule')} Computer: {event.get('computer')} Event ID: {event.get('event_id')} Timestamp: {event.get('timestamp')} Severity: {rule.get('level', 'unknown')}")
    
    # Save results to JSON file
    results_data = {
        "matches": matches,
        "matched_rules": list(matched_rule_ids),
        "total_matches": len(matches)
    }
    
    # Ensure detection_results directory exists
    results_dir = "data/detection_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Save to file
    results_file = os.path.join(results_dir, "sigma_matches.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"Detection Summary:")
    print(f"Total Matches: {len(matches)}")
    print(f"Unique Rules Matched: {len(matched_rule_ids)}")
    print(f"Results saved to: {results_file}")
    print(f"{'='*60}")
    
    return results_data

def main():
    import json
    events_file = "data/processed/normalized/Security_normalized.json"
    rules_folder = "analysis/detection/sigma/rules"
    if not os.path.exists(events_file):
        print("Error: Events file not found at", events_file)
        return
    if not os.path.exists(rules_folder):
        print("Error: Rules directory not found at", rules_folder)
        return
    with open(events_file, 'r', encoding='utf-8') as f:
        log_events = json.load(f)
    results = run_sigma_pipeline(log_events, rules_folder)
    return results

if __name__ == "__main__":
    main()
