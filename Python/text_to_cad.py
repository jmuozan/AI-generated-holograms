from typing import Any, List, Optional, Tuple, Union

from kittycad.api.ai import create_text_to_cad, get_text_to_cad_model_for_user
from kittycad.models import Error, TextToCad
from kittycad.models.file_export_format import FileExportFormat
from kittycad.models.text_to_cad_create_body import TextToCadCreateBody
from kittycad.types import Response

import base64

def text_to_cad_create(prompt, client):

    result: Optional[Union[TextToCad, Error]] = create_text_to_cad.sync(
        client=client,
        output_format=FileExportFormat.STL,
        body=TextToCadCreateBody(
            prompt=prompt,
        ),
    )

    if isinstance(result, Error) or result == None:
        print(result)
        raise Exception("Error in response")

    body: TextToCad = result
    print(body.id)
    return body.id


def get_text_to_cad_model(generation_id, client):
    result: Optional[
        Union[TextToCad, Error]
    ] = get_text_to_cad_model_for_user.sync(
        client=client,
        id=generation_id,
    )

    if isinstance(result, Error) or result == None:
        print(result)
        raise Exception("Error in response")

    body: TextToCad = result
    return body


def decode_stl(cad_response_body):
    print(list(cad_response_body.outputs.keys()))
    try:
        # Directly access the 'source.stl' item
        base64_data_obj = cad_response_body.outputs['source.stl']
        base64_stl_string = base64_data_obj.get_encoded()

        # Pad the Base64 string if necessary
        padding_needed = len(base64_stl_string) % 4
        if padding_needed:
            base64_stl_string += "=" * (4 - padding_needed)

        # Decode the Base64 string
        stl_binary = base64.b64decode(base64_stl_string)
        return stl_binary

    except Exception as e:
        print(f"An error occurred: {e}")
        # Handle the error or return None (or an empty byte string) to indicate failure
        return None
