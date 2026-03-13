INSTANCE_COST = 5000

def analyze_resources(df):

    avg_cpu = df["cpu_usage"].mean()

    if avg_cpu < 30:
        required_instances = 4
    elif avg_cpu < 50:
        required_instances = 6
    elif avg_cpu < 70:
        required_instances = 8
    else:
        required_instances = 10

    optimized_cost = required_instances * INSTANCE_COST

    return {
        "required_instances": required_instances,
        "optimized_cost": optimized_cost
    }