import json
import VRP_Gen_5 as gen


def lambda_handler(event, context):
    # TODO implement
    resp = gen.vrp_generator(event)

    return {
        'statusCode': 200,
        'body': json.dumps(resp)
    }
