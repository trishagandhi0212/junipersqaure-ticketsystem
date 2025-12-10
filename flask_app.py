"""
Complete Flask Web Application for Ticket Triage
Creates a full website with HTML interface

Setup:
1. pip install flask
2. Create 'templates' folder in same directory
3. Save HTML template (see instructions below)
4. python flask_app.py
5. Open http://localhost:5000
"""

from flask import Flask, render_template_string, request
from dataclasses import dataclass
from typing import List
from enum import Enum

app = Flask(__name__)


class Priority(Enum):
    URGENT = "Urgent"
    CRITICAL = "Critical"
    HIGH = "High"
    NORMAL = "Normal"
    LOW = "Low"


class Sentiment(Enum):
    VERY_NEGATIVE = "Very Negative"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"
    POSITIVE = "Positive"


@dataclass
class Ticket:
    id: int
    subject: str
    body: str
    priority: str = None
    priority_score: int = 0
    sentiment: str = None
    categories: List[str] = None
    action_type: str = None
    urgency: int = 0
    financial_impact: int = 0
    blocking: int = 0


def analyze_ticket(ticket_data: dict) -> Ticket:
    """Analyze a single ticket"""
    text = f"{ticket_data['subject']} {ticket_data['body']}".lower()
    
    # Urgency detection
    urgency = 3
    if any(word in text for word in ['today', '5 pm', 'by ']):
        urgency = 10
    elif any(word in text for word in ['missing', 'where is', '??']):
        urgency = 9
    elif any(word in text for word in ['error', '500']):
        urgency = 7
    elif any(word in text for word in ['login', "can't", 'trying to']):
        urgency = 7
    elif any(word in text for word in ['feature', 'would be great']):
        urgency = 1
    
    # Financial impact
    financial_impact = 0
    if 'distribution' in text and any(word in text for word in ['missing', 'where is']):
        financial_impact = 10
    elif any(word in text for word in ['distribution', 'bank', 'account']):
        financial_impact = 8
    elif any(word in text for word in ['k-1', 'tax']):
        financial_impact = 7
    elif any(word in text for word in ['login', 'access']):
        financial_impact = 3
    
    # User blocking
    blocking = 0
    if "can't" in text or 'trying to log in' in text:
        blocking = 10
    elif any(word in text for word in ['error', '500']):
        blocking = 7
    elif any(word in text for word in ['update', 'please']):
        blocking = 3
    
    # Sentiment analysis
    sentiment_value = 0
    sentiment = Sentiment.NEUTRAL.value
    
    if any(word in text for word in ['unacceptable', '??', 'angry']):
        sentiment_value = -3
        sentiment = Sentiment.VERY_NEGATIVE.value
    elif any(word in text for word in ['need this', 'checked spam']):
        sentiment_value = -2
        sentiment = Sentiment.NEGATIVE.value
    elif any(word in text for word in ['great', 'just a thought']):
        sentiment_value = 1
        sentiment = Sentiment.POSITIVE.value
    
    # Calculate priority score
    priority_score = (urgency * 3) + (financial_impact * 3) + (blocking * 2) + sentiment_value
    
    # Determine priority level
    if priority_score >= 50:
        priority = Priority.URGENT.value
    elif priority_score >= 45:
        priority = Priority.CRITICAL.value
    elif priority_score >= 35:
        priority = Priority.HIGH.value
    elif priority_score >= 20:
        priority = Priority.NORMAL.value
    else:
        priority = Priority.LOW.value
    
    # Categorization
    categories = []
    if any(word in text for word in ['login', 'password', 'access']):
        categories.append('Authentication')
    if any(word in text for word in ['k-1', 'tax']):
        categories.append('Tax Documents')
    if any(word in text for word in ['bank', 'account']):
        categories.append('Banking')
    if 'distribution' in text:
        categories.append('Distributions')
    if any(word in text for word in ['error', '500']):
        categories.append('Technical Issue')
    if any(word in text for word in ['feature', 'would be great']):
        categories.append('Feature Request')
    if any(word in text for word in ['export', 'report']):
        categories.append('Reporting')
    if any(word in text for word in ['unacceptable', '??']):
        categories.append('Escalation')
    
    # Action type
    if priority in [Priority.URGENT.value, Priority.CRITICAL.value]:
        action_type = 'Immediate Response Required'
    elif 'Technical Issue' in categories:
        action_type = 'Engineering Investigation'
    elif 'Feature Request' in categories:
        action_type = 'Product Backlog'
    elif any(cat in categories for cat in ['Banking', 'Distributions']):
        action_type = 'Account Management'
    else:
        action_type = 'Standard Support'
    
    return Ticket(
        id=ticket_data['id'],
        subject=ticket_data['subject'],
        body=ticket_data['body'],
        priority=priority,
        priority_score=priority_score,
        sentiment=sentiment,
        categories=categories,
        action_type=action_type,
        urgency=urgency,
        financial_impact=financial_impact,
        blocking=blocking
    )


# Sample tickets
SAMPLE_TICKETS = [
    {
        "id": 101,
        "subject": "Login help",
        "body": "I'm trying to log in to see my K-1s but the password link isn't arriving. I checked spam. I need this for my accountant by 5 PM today."
    },
    {
        "id": 102,
        "subject": "Bank Update",
        "body": "Please update my distribution instructions. I want my dividends sent to my new Chase account ending in 4490. Attached is a voided check."
    },
    {
        "id": 103,
        "subject": "Platform Error",
        "body": "I'm getting a 500 error when I try to export the 'Q3 Performance Report' PDF. I've tried on Chrome and Safari. Screenshot attached."
    },
    {
        "id": 104,
        "subject": "Angry / Missing Funds",
        "body": "Where is my distribution?? It was supposed to hit yesterday. This is unacceptable. I've been an investor for 5 years and never seen such a delay."
    },
    {
        "id": 105,
        "subject": "Feature Request",
        "body": "It would be great if I could sort my investments by 'Vintage Year' on the dashboard. Just a thought!"
    }
]


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Juniper Square Ticket Triage System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #004646 0%, #059669 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
            border-top: 5px solid #004646;
        }
        .header h1 {
            color: #004646;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        .triage-btn {
            background: #059669;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.2em;
            border-radius: 8px;
            cursor: pointer;
            margin: 20px 0;
            transition: all 0.3s;
        }
        .triage-btn:hover {
            background: #004646;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .ticket {
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s;
            border-left: 5px solid #059669;
        }
        .ticket:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            border-left-color: #004646;
        }
        .ticket-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            flex-wrap: wrap;
            gap: 10px;
        }
        .queue-number {
            font-size: 2em;
            font-weight: bold;
            color: #059669;
        }
        .priority-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }
        .priority-Urgent {
            background: #ffebee;
            color: #c62828;
            border: 2px solid #c62828;
        }
        .priority-Critical {
            background: #fff3e0;
            color: #e65100;
            border: 2px solid #e65100;
        }
        .priority-High {
            background: #fffde7;
            color: #f57f17;
            border: 2px solid #f57f17;
        }
        .priority-Normal {
            background: #e8f5e9;
            color: #059669;
            border: 2px solid #059669;
        }
        .priority-Low {
            background: #fafafa;
            color: #757575;
            border: 2px solid #bdbdbd;
        }
        .ticket-subject {
            font-size: 1.5em;
            font-weight: bold;
            color: #004646;
            margin-bottom: 10px;
        }
        .ticket-body {
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        .ticket-meta {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        .meta-item {
            background: #f5f5f5;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.9em;
            border-left: 3px solid #DEA68B;
        }
        .category-tag {
            background: #e8f5f0;
            color: #004646;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.85em;
            display: inline-block;
            margin: 3px;
            border: 1px solid #059669;
        }
        .score-breakdown {
            background: #fafafa;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 0.9em;
            border: 1px solid #DEA68B;
        }
        .score-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
        }
        .summary {
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-top: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-top: 5px solid #004646;
        }
        .summary h2 {
            margin-bottom: 20px;
            color: #004646;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .summary-card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border: 2px solid;
        }
        .summary-card h3 {
            font-size: 2em;
            margin-bottom: 5px;
        }
        .summary-urgent { 
            background: #ffebee; 
            color: #c62828;
            border-color: #c62828;
        }
        .summary-critical { 
            background: #fff3e0; 
            color: #e65100;
            border-color: #e65100;
        }
        .summary-high { 
            background: #fffde7; 
            color: #f57f17;
            border-color: #f57f17;
        }
        .summary-normal { 
            background: #e8f5e9; 
            color: #059669;
            border-color: #059669;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Juniper Square Ticket Triage System</h1>
            <p>Automatically prioritize support tickets using intelligent analysis</p>
            
            {% if not tickets %}
            <form method="POST" action="/">
                <button type="submit" class="triage-btn">Start AI Triage</button>
            </form>
            {% else %}
            <div style="margin-top: 20px;">
                <span style="color: #059669; font-size: 1.2em;">✓ Triage Complete!</span>
                <form method="GET" action="/" style="display: inline;">
                    <button type="submit" class="triage-btn" style="background: #DEA68B; margin-left: 10px;">Reset</button>
                </form>
            </div>
            {% endif %}
        </div>

        {% if tickets %}
        <div>
            {% for ticket in tickets %}
            <div class="ticket">
                <div class="ticket-header">
                    <div class="queue-number">#{{ loop.index }}</div>
                    <div class="priority-badge priority-{{ ticket.priority.replace(' ', '') }}">
                        {{ ticket.priority }} (Score: {{ ticket.priority_score }})
                    </div>
                </div>
                
                <div class="ticket-subject">Ticket #{{ ticket.id }}: {{ ticket.subject }}</div>
                <div class="ticket-body">{{ ticket.body }}</div>
                
                <div class="ticket-meta">
                    <div class="meta-item"><strong>Sentiment:</strong> {{ ticket.sentiment }}</div>
                    <div class="meta-item"><strong>Action:</strong> {{ ticket.action_type }}</div>
                </div>
                
                <div style="margin-top: 10px;">
                    {% for category in ticket.categories %}
                    <span class="category-tag">{{ category }}</span>
                    {% endfor %}
                </div>
                
                <div class="score-breakdown">
                    <strong>Scoring Breakdown:</strong>
                    <div class="score-item">
                        <span>Urgency ({{ ticket.urgency }}/10):</span>
                        <span><strong>{{ ticket.urgency * 3 }} pts</strong></span>
                    </div>
                    <div class="score-item">
                        <span>Financial Impact ({{ ticket.financial_impact }}/10):</span>
                        <span><strong>{{ ticket.financial_impact * 3 }} pts</strong></span>
                    </div>
                    <div class="score-item">
                        <span>User Blocking ({{ ticket.blocking }}/10):</span>
                        <span><strong>{{ ticket.blocking * 2 }} pts</strong></span>
                    </div>
                    <div class="score-item" style="border-top: 2px solid #DEA68B; margin-top: 5px; padding-top: 5px;">
                        <span>Total Score:</span>
                        <span style="color: #059669;"><strong>{{ ticket.priority_score }} pts</strong></span>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="summary">
            <h2>Summary Statistics</h2>
            <div class="summary-grid">
                <div class="summary-card summary-urgent">
                    <h3>{{ summary.urgent }}</h3>
                    <p>Urgent Tickets</p>
                </div>
                <div class="summary-card summary-critical">
                    <h3>{{ summary.critical }}</h3>
                    <p>Critical Tickets</p>
                </div>
                <div class="summary-card summary-high">
                    <h3>{{ summary.high }}</h3>
                    <p>High Priority</p>
                </div>
                <div class="summary-card summary-normal">
                    <h3>{{ summary.normal + summary.low }}</h3>
                    <p>Normal/Low</p>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    tickets = None
    summary = None
    
    if request.method == 'POST':
        # Analyze all tickets
        analyzed = [analyze_ticket(ticket) for ticket in SAMPLE_TICKETS]
        
        # Sort by priority score
        analyzed.sort(key=lambda t: t.priority_score, reverse=True)
        
        tickets = analyzed
        
        # Calculate summary
        summary = {
            'urgent': sum(1 for t in tickets if t.priority == 'Urgent'),
            'critical': sum(1 for t in tickets if t.priority == 'Critical'),
            'high': sum(1 for t in tickets if t.priority == 'High'),
            'normal': sum(1 for t in tickets if t.priority == 'Normal'),
            'low': sum(1 for t in tickets if t.priority == 'Low')
        }
    
    return render_template_string(HTML_TEMPLATE, tickets=tickets, summary=summary)


if __name__ == '__main__':
    print("\n🚀 Starting Ticket Triage Web Application...")
    print("📍 Open your browser to: http://localhost:5000")
    print("💡 Click 'Start AI Triage' to analyze tickets\n")
    app.run(debug=True, port=5000)