def aggregate_by_ip(outputs, intermediate_data):
    """
    :param outputs: [(k3, v3)] where k3 and v3 are output data
    which can be of any type
    :param intermediate_data: (k2, [v2]) where k2 and v2 are intermediate data
    which can be of any type
    """

    key, values = intermediate_data

    revenue_sum = 0
    try:
        for value in values:
            revenue_sum += float(value)

        outputs.append((key, [revenue_sum]))
    except Exception as e:
        print("type error: " + str(e))
