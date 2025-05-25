# sales_agent/evaluation/golden_dataset.py

from typing import List, Dict

GOLDEN_DATASET = [
    {
        "id": "ex1",
        "conversation_history": [
            {"sender": "prospect", "content": "I looked at your pricing page and it's a bit confusing.", "timestamp": "2024-01-01T10:00:00"},
            {"sender": "agent", "content": "Happy to clarify! Are you referring to our enterprise tier?", "timestamp": "2024-01-01T10:01:00"},
        ],
        "current_prospect_message": "Yeah, how does the enterprise plan differ from pro?",
        "prospect_id": "123",
        "ground_truth": {
            "intent": "pricing_comparison",
            "entities": ["enterprise plan", "pro plan"],
            "tools_to_call": [
                {
                    "tool": "query_knowledge_base",
                    "query": "difference between enterprise plan and pro plan"
                }
            ],
            "suggested_response_draft": "Sure! The enterprise plan includes advanced analytics, dedicated support, and API access — which the pro plan doesn’t.",
            "internal_next_steps": [
                {"action": "SCHEDULE_FOLLOW_UP", "details": {"reason": "answered pricing query"}}
            ]
        }
    },
    {
        "id": "ex2",
        "conversation_history": [],
        "current_prospect_message": "Can your platform integrate with Salesforce?",
        "prospect_id": "124",
        "ground_truth": {
            "intent": "integration_query",
            "entities": ["Salesforce"],
            "tools_to_call": [
                {"tool": "query_knowledge_base", "query": "Salesforce integration"}
            ],
            "suggested_response_draft": "Yes, our platform has native integration with Salesforce. You can sync leads and activities directly.",
            "internal_next_steps": [{"action": "UPDATE_CRM", "details": {"field": "interest_in_integration", "value": "Salesforce"}}]
        }
    },
    {
        "id": "ex3",
        "conversation_history": [
            {"sender": "prospect", "content": "We've tried similar tools before.", "timestamp": "2024-01-01T09:00:00"}
        ],
        "current_prospect_message": "How do you compare with HubSpot?",
        "prospect_id": "125",
        "ground_truth": {
            "intent": "competitor_comparison",
            "entities": ["HubSpot"],
            "tools_to_call": [
                {"tool": "query_knowledge_base", "query": "comparison with HubSpot"}
            ],
            "suggested_response_draft": "Compared to HubSpot, our tool offers more granular workflow automation and better reporting customization.",
            "internal_next_steps": [{"action": "FLAG_FOR_HUMAN_REVIEW", "details": {"reason": "prospect evaluating competitors"}}]
        }
    },
    {
        "id": "ex4",
        "conversation_history": [],
        "current_prospect_message": "I’m not sure your product is secure enough for a healthcare use case.",
        "prospect_id": "126",
        "ground_truth": {
            "intent": "security_concern",
            "entities": ["healthcare", "security"],
            "tools_to_call": [
                {"tool": "query_knowledge_base", "query": "security compliance for healthcare"}
            ],
            "suggested_response_draft": "Great point. We’re HIPAA-compliant and have SOC 2 Type II certification to ensure data security.",
            "internal_next_steps": [{"action": "SCHEDULE_FOLLOW_UP", "details": {"reason": "addressed security concern"}}]
        }
    },
    {
        "id": "ex5",
        "conversation_history": [
            {"sender": "prospect", "content": "We’re currently using spreadsheets to manage this.", "timestamp": "2024-01-01T11:00:00"}
        ],
        "current_prospect_message": "How much time would we save with automation?",
        "prospect_id": "127",
        "ground_truth": {
            "intent": "efficiency_inquiry",
            "entities": ["automation", "spreadsheets"],
            "tools_to_call": [
                {"tool": "query_knowledge_base", "query": "time savings with automation"}
            ],
            "suggested_response_draft": "Customers typically report saving 5-10 hours per week by automating manual spreadsheet processes.",
            "internal_next_steps": [{"action": "UPDATE_CRM", "details": {"field": "pain_point", "value": "manual workflows"}}]
        }
    },
    {
        "id": "ex6",
        "conversation_history": [],
        "current_prospect_message": "Do you offer training for new users?",
        "prospect_id": "128",
        "ground_truth": {
            "intent": "onboarding_query",
            "entities": ["training", "onboarding"],
            "tools_to_call": [
                {"tool": "query_knowledge_base", "query": "user training and onboarding support"}
            ],
            "suggested_response_draft": "Absolutely. We provide onboarding sessions, tutorial videos, and a dedicated customer success manager.",
            "internal_next_steps": [{"action": "NO_ACTION", "details": {}}]
        }
    },
    {
        "id": "ex7",
        "conversation_history": [],
        "current_prospect_message": "Just checking in — did you get a chance to review my last question?",
        "prospect_id": "129",
        "ground_truth": {
            "intent": "follow_up",
            "entities": [],
            "tools_to_call": [],
            "suggested_response_draft": "Thanks for the nudge! Let me get back to your last question right away.",
            "internal_next_steps": [{"action": "FLAG_FOR_HUMAN_REVIEW", "details": {"reason": "manual intervention likely needed"}}]
        }
    },
    {
        "id": "ex8",
        "conversation_history": [
            {"sender": "prospect", "content": "We’re a team of 10, but might grow soon.", "timestamp": "2024-01-01T10:20:00"}
        ],
        "current_prospect_message": "Would your pricing change as we scale?",
        "prospect_id": "130",
        "ground_truth": {
            "intent": "scalability_pricing",
            "entities": ["pricing", "scaling"],
            "tools_to_call": [
                {"tool": "query_knowledge_base", "query": "pricing for growing teams"}
            ],
            "suggested_response_draft": "Yes, our pricing is tiered based on team size, so as you grow, we’ll adjust accordingly — often with volume discounts.",
            "internal_next_steps": [{"action": "UPDATE_CRM", "details": {"field": "team_size", "value": "10+"}}]
        }
    },
    {
        "id": "ex9",
        "conversation_history": [
            {"sender": "prospect", "content": "Can I get a free trial to test things out?", "timestamp": "2024-01-02T09:00:00"}
        ],
        "current_prospect_message": "Just want to try it before committing.",
        "prospect_id": "124",
        "ground_truth": {
            "intent": "trial_request",
            "entities": ["free trial"],
            "tools_to_call": [],
            "suggested_response_draft": "Absolutely! We offer a 14-day free trial — I can help you get started.",
            "internal_next_steps": [{"action": "SCHEDULE_FOLLOW_UP", "details": {"reason": "trial initiated"}}]
        }
    },
    {
        "id": "ex10",
        "conversation_history": [
            {"sender": "prospect", "content": "Does it support real-time analytics?", "timestamp": "2024-01-03T11:30:00"}
        ],
        "current_prospect_message": "Real-time data matters a lot to us.",
        "prospect_id": "125",
        "ground_truth": {
            "intent": "feature_inquiry",
            "entities": ["real-time analytics"],
            "tools_to_call": [
                {"tool": "query_knowledge_base", "query": "real-time analytics support"}
            ],
            "suggested_response_draft": "Yes, our platform offers real-time analytics dashboards that update live as events happen.",
            "internal_next_steps": [{"action": "UPDATE_CRM", "details": {"field": "feature_interest", "value": "real-time analytics"}}]
        }
    },
    {
        "id": "ex11",
        "conversation_history": [
            {"sender": "prospect", "content": "It seems a bit pricey compared to other tools.", "timestamp": "2024-01-04T14:10:00"}
        ],
        "current_prospect_message": "Why should I pay more?",
        "prospect_id": "126",
        "ground_truth": {
            "intent": "objection_handling",
            "entities": ["pricing", "competitors"],
            "tools_to_call": [
                {"tool": "query_knowledge_base", "query": "value vs competitors"}
            ],
            "suggested_response_draft": "We understand. Our pricing includes dedicated support, faster implementation, and customizable workflows, which many competitors don’t offer.",
            "internal_next_steps": [{"action": "FLAG_FOR_HUMAN_REVIEW", "details": {"reason": "pricing objection"}}]
        }
    },
    {
        "id": "ex12",
        "conversation_history": [
            {"sender": "prospect", "content": "Would this work for a marketing automation workflow?", "timestamp": "2024-01-05T15:00:00"}
        ],
        "current_prospect_message": "We need something for automating email and lead scoring.",
        "prospect_id": "127",
        "ground_truth": {
            "intent": "use_case_validation",
            "entities": ["marketing automation", "lead scoring"],
            "tools_to_call": [
                {"tool": "query_knowledge_base", "query": "use case marketing automation"}
            ],
            "suggested_response_draft": "Yes, our platform is often used for marketing automation and integrates well with CRMs for lead scoring.",
            "internal_next_steps": []
        }
    },
    {
        "id": "ex13",
        "conversation_history": [
            {"sender": "prospect", "content": "When does our subscription renew?", "timestamp": "2024-01-06T10:45:00"}
        ],
        "current_prospect_message": "Need to plan budget for next quarter.",
        "prospect_id": "128",
        "ground_truth": {
            "intent": "renewal_question",
            "entities": ["subscription", "renewal"],
            "tools_to_call": [
                {"tool": "fetch_prospect_details", "query": "renewal_date for prospect_id 128"}
            ],
            "suggested_response_draft": "Your subscription is set to renew on March 15. Let me know if you'd like to make any changes.",
            "internal_next_steps": [{"action": "UPDATE_CRM", "details": {"field": "renewal_interest", "value": "confirmed"}}]
        }
    },
    {
        "id": "ex14",
        "conversation_history": [
            {"sender": "prospect", "content": "Do you have a deployment guide?", "timestamp": "2024-01-07T16:00:00"}
        ],
        "current_prospect_message": "We’d like to get started soon.",
        "prospect_id": "129",
        "ground_truth": {
            "intent": "deployment_help",
            "entities": ["deployment guide"],
            "tools_to_call": [
                {"tool": "query_knowledge_base", "query": "deployment guide"}
            ],
            "suggested_response_draft": "Yes, here's the step-by-step deployment guide to help your team get started quickly.",
            "internal_next_steps": [{"action": "SCHEDULE_FOLLOW_UP", "details": {"reason": "shared deployment materials"}}]
        }
    },
    {
        "id": "ex15",
        "conversation_history": [
            {"sender": "prospect", "content": "I keep getting an error when I try to log in.", "timestamp": "2024-01-09T09:00:00"}
        ],
        "current_prospect_message": "It just shows a blank screen.",
        "prospect_id": "131",
        "ground_truth": {
            "intent": "technical_issue",
            "entities": ["login error"],
            "tools_to_call": [],
            "suggested_response_draft": "Thanks for reporting this — can you share a screenshot or the exact error message? I’ll escalate this to our support team immediately.",
            "internal_next_steps": [{"action": "FLAG_FOR_HUMAN_REVIEW", "details": {"reason": "technical issue"}}]
        }
    },
]
