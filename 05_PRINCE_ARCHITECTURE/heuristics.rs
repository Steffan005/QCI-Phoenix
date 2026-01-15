use std::collections::HashMap;
use regex::Regex;
use serde::{Serialize, Deserialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct HeuristicResult {
    pub score: f64,
    pub passed: bool,
    pub violations: Vec<String>,
    pub details: HashMap<String, serde_json::Value>,
}

pub struct HeuristicValidator {
    regex_bans: Vec<(String, Regex)>,
    adversarial_patterns: Vec<(String, Regex)>,
}

impl HeuristicValidator {
    pub fn new() -> Self {
        let bans = vec![
            ("shell_deletion", r"rm\s+-[rf]+\s+/"),
            ("shell_dangerous", r"(sudo|chmod\s+777|mkfs|dd\s+if=)"),
            ("secrets_exfil", r"(curl|wget|nc)\s+.*\.(env|key|secret|token)"),
            ("code_injection", r"eval\(|exec\(|__import__\("),
            ("path_traversal", r"\.\./\.\./"),
            ("credential_leak", r#"(password|api_key|secret)\s*=\s*['"][^'"]+['"]"#),
        ];

        let adversarial = vec![
            ("prompt_injection", r"ignore\s+(previous|all)\s+instructions"),
            ("infinite_loop", r"while\s+True\s*:|for\s+\w+\s+in\s+itertools\.count\(\)"),
            ("resource_surge", r"(multiprocessing\.Pool|threading\.Thread).*range\(\d{4,}\)"),
            ("unsafe_action", r"os\.(system|popen|execv|fork)\s*\("),
        ];

        let compile = |list: Vec<(&str, &str)>| {
            list.into_iter()
                .map(|(name, pattern)| (name.to_string(), Regex::new(pattern).unwrap()))
                .collect()
        };

        Self {
            regex_bans: compile(bans),
            adversarial_patterns: compile(adversarial),
        }
    }

    pub fn validate(&self, text: &str) -> HeuristicResult {
        let mut violations = Vec::new();
        let mut details = HashMap::new();

        // 1. Regex Bans
        for (name, re) in &self.regex_bans {
            if re.is_match(text) {
                violations.push(format!("regex_ban:{}", name));
            }
        }

        if !violations.is_empty() {
            return HeuristicResult {
                score: 0.0,
                passed: false,
                violations,
                details,
            };
        }

        // 2. Adversarial
        for (name, re) in &self.adversarial_patterns {
            if re.is_match(text) {
                violations.push(format!("adversarial:{}", name));
            }
        }

        if !violations.is_empty() {
            return HeuristicResult {
                score: 0.0,
                passed: false,
                violations,
                details,
            };
        }

        // 3. Entropy
        let (entropy_score, entropy_flag) = self.check_entropy(text);
        details.insert("entropy".to_string(), serde_json::json!({
            "score": entropy_score,
            "flag": entropy_flag
        }));
        
        if let Some(flag) = entropy_flag {
            violations.push(format!("entropy_{}", flag));
        }

        // Composite Score (simplified)
        let composite_score = entropy_score; // Add length checks later if needed

        HeuristicResult {
            score: composite_score,
            passed: composite_score > 0.5 && violations.is_empty(),
            violations,
            details,
        }
    }

    fn check_entropy(&self, text: &str) -> (f64, Option<String>) {
        // Allow short inputs for chat (e.g. "hi", "yes", "no")
        if text.len() < 2 {
            return (0.5, Some("too_short".to_string()));
        }
        if text.len() < 10 {
            return (1.0, None); // Pass short messages
        }

        let chars: Vec<char> = text.chars().collect();
        let mut counts = HashMap::new();
        let mut total = 0;

        for window in chars.windows(2) {
            let pair: String = window.iter().collect();
            *counts.entry(pair).or_insert(0) += 1;
            total += 1;
        }

        if total == 0 {
            return (0.5, Some("too_short".to_string()));
        }

        let mut entropy = 0.0;
        for count in counts.values() {
            let p = *count as f64 / total as f64;
            entropy -= p * p.log2();
        }

        let max_entropy = 11.0;
        let normalized = (entropy / max_entropy).min(1.0);

        let flag = if normalized < 0.2 {
            Some("ultra_low".to_string())
        } else if normalized > 0.95 {
            Some("ultra_high".to_string())
        } else {
            None
        };

        let score = if normalized < 0.2 {
            0.3
        } else if normalized > 0.95 {
            0.5
        } else {
            1.0
        };

        (score, flag)
    }
}
