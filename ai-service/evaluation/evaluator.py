from evaluation.scenarios.scenarios import scenarios

from app.agent import run_agent


# ---------------------------------------------------------
# Compare tool arguments
# ---------------------------------------------------------

def arguments_match(actual_arguments, expected_arguments):

    return actual_arguments == expected_arguments


# ---------------------------------------------------------
# Find policy status from tool results
# ---------------------------------------------------------

def get_policy_status(result):

    for tool_result in result["tool_results"]:

        if tool_result["name"] != "create_payment_intent":
            continue

        payment_result = tool_result["result"]

        payment_intent = payment_result.get(
            "payment_intent"
        )

        if payment_intent is None:
            return None

        return payment_intent.get("status")

    return None


# ---------------------------------------------------------
# Evaluate one scenario
# ---------------------------------------------------------

def evaluate_scenario(scenario):

    result = run_agent(
        scenario["input"]
    )

    tool_calls = result["tool_calls"]

    expected_tool = scenario["expected_tool"]

    # -----------------------------------------------------
    # Tool selection
    # -----------------------------------------------------

    actual_tools = [
        tool["name"]
        for tool in tool_calls
    ]

    tool_selection_pass = (
            expected_tool in actual_tools
    )

    # -----------------------------------------------------
    # Tool arguments
    # -----------------------------------------------------

    argument_pass = False
    actual_arguments = None

    matching_tool_calls = [
        tool
        for tool in tool_calls
        if tool["name"] == expected_tool
    ]

    if matching_tool_calls:

        actual_arguments = matching_tool_calls[0]["arguments"]

        argument_pass = arguments_match(
            actual_arguments,
            scenario["expected_arguments"]
        )

    # -----------------------------------------------------
    # Policy outcome
    # -----------------------------------------------------

    expected_policy_status = scenario.get(
        "expected_policy_status"
    )

    actual_policy_status = None
    policy_pass = True

    if expected_policy_status:

        actual_policy_status = get_policy_status(
            result
        )

        policy_pass = (
                actual_policy_status
                == expected_policy_status
        )

    # -----------------------------------------------------
    # Overall scenario result
    # -----------------------------------------------------

    scenario_pass = (
            tool_selection_pass
            and argument_pass
            and policy_pass
    )

    return {
        "id": scenario["id"],
        "name": scenario["name"],
        "expected_tool": expected_tool,
        "actual_tools": actual_tools,
        "tool_selection": (
            "PASS"
            if tool_selection_pass
            else "FAIL"
        ),
        "expected_arguments": (
            scenario["expected_arguments"]
        ),
        "actual_arguments": actual_arguments,
        "tool_arguments": (
            "PASS"
            if argument_pass
            else "FAIL"
        ),
        "expected_policy_status": (
            expected_policy_status
        ),
        "actual_policy_status": (
            actual_policy_status
        ),
        "policy_compliance": (
            "PASS"
            if policy_pass
            else "FAIL"
        ),
        "scenario_result": (
            "PASS"
            if scenario_pass
            else "FAIL"
        ),
        "final_answer": result["final_answer"]
    }


# ---------------------------------------------------------
# Run complete evaluation
# ---------------------------------------------------------

def run_evaluation():

    results = []

    print("\n")
    print("=" * 75)
    print("FINAGENT LAB - AGENT EVALUATION")
    print("=" * 75)

    for scenario in scenarios:

        print("\n")
        print("-" * 75)

        print(
            f"{scenario['id']} - {scenario['name']}"
        )

        print(
            f"Input: {scenario['input']}"
        )

        result = evaluate_scenario(
            scenario
        )

        results.append(result)

        print(
            f"Expected tool: "
            f"{result['expected_tool']}"
        )

        print(
            f"Actual tools: "
            f"{result['actual_tools']}"
        )

        print(
            f"Tool selection: "
            f"{result['tool_selection']}"
        )

        print(
            f"Expected arguments: "
            f"{result['expected_arguments']}"
        )

        print(
            f"Actual arguments: "
            f"{result['actual_arguments']}"
        )

        print(
            f"Tool arguments: "
            f"{result['tool_arguments']}"
        )

        if result["expected_policy_status"]:

            print(
                f"Expected policy: "
                f"{result['expected_policy_status']}"
            )

            print(
                f"Actual policy: "
                f"{result['actual_policy_status']}"
            )

            print(
                f"Policy compliance: "
                f"{result['policy_compliance']}"
            )

        print(
            f"Scenario result: "
            f"{result['scenario_result']}"
        )

    # -----------------------------------------------------
    # Calculate metrics
    # -----------------------------------------------------

    total = len(results)

    tool_selection_passed = sum(
        1
        for result in results
        if result["tool_selection"] == "PASS"
    )

    argument_passed = sum(
        1
        for result in results
        if result["tool_arguments"] == "PASS"
    )

    policy_scenarios = [
        result
        for result in results
        if result["expected_policy_status"]
    ]

    policy_passed = sum(
        1
        for result in policy_scenarios
        if result["policy_compliance"] == "PASS"
    )

    scenario_passed = sum(
        1
        for result in results
        if result["scenario_result"] == "PASS"
    )

    tool_selection_accuracy = (
        (tool_selection_passed / total) * 100
        if total > 0
        else 0
    )

    tool_argument_accuracy = (
        (argument_passed / total) * 100
        if total > 0
        else 0
    )

    policy_compliance = (
        (policy_passed / len(policy_scenarios)) * 100
        if policy_scenarios
        else 100
    )

    scenario_success_rate = (
        (scenario_passed / total) * 100
        if total > 0
        else 0
    )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print("\n")
    print("=" * 75)
    print("EVALUATION SUMMARY")
    print("=" * 75)

    print(
        f"Total scenarios:          {total}"
    )

    print(
        f"Scenarios passed:         {scenario_passed}"
    )

    print(
        f"Scenarios failed:         "
        f"{total - scenario_passed}"
    )

    print(
        f"Tool Selection Accuracy:  "
        f"{tool_selection_accuracy:.2f}%"
    )

    print(
        f"Tool Argument Accuracy:   "
        f"{tool_argument_accuracy:.2f}%"
    )

    print(
        f"Policy Compliance:        "
        f"{policy_compliance:.2f}%"
    )

    print(
        f"Scenario Success Rate:    "
        f"{scenario_success_rate:.2f}%"
    )

    print("=" * 75)

    return results


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    run_evaluation()