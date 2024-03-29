def extract_ip_and_revenue(outputs, input_pair):
    """
    :param outputs: [(k2, v2)] where k2 and v2 are intermediate data
    which can be of any type
    :param input_pair: (k1, v1) where k1 and v1 are assumed to be of type string
    """
    try:
        _, line = input_pair
        data = line.split(',')
        src_ip = data[0]
        ad_revenue = float(data[3])
        outputs.append(tuple((src_ip, ad_revenue)))
    except Exception as e:
        print("type error: " + str(e))
