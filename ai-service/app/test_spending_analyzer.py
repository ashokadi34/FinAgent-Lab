from app.data.transactions import transactions
from app.guardrails.spending_analyzer import analyze_spending


result = analyze_spending(
    transactions["ACC001"]
)

print("Spending Analysis:")
print(result)