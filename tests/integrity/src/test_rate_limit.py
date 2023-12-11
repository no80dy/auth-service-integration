import uuid
import pytest


HTTP_403 = 403
HTTP_429 = 429


@pytest.mark.parametrize(
    'request_data, response_data',
    [
        (
            {'requests_count': 1},
            {'status': HTTP_403}
        ),
        (
            {'requests_count': 21},
            {'status': HTTP_429}
        ),
        (
            {'requests_count': 28},
            {'status': HTTP_429}
        )
    ]
)
async def test_rate_limit(
    make_get_request,
    request_data,
    response_data
):
    for i in range(request_data['requests_count']):
        response = await make_get_request(f"persons/{uuid.uuid4()}", {}, {})
    assert response['status'] == response_data['status']

