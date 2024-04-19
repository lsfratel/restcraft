import re

from restcraft.core.routing.router import router


def url_for(view_name: str, **kwargs) -> str:
    """
    Generate a URL string for a named route, replacing any dynamic parameters
    in the route pattern with the provided keyword arguments.

    Args:
        view_name (str): The name of the view/route to generate the URL for.
        **kwargs: Keyword arguments that correspond to the dynamic parameters
            in the route pattern.

    Returns:
        str: The generated URL string.

    Raises:
        ValueError: If a required parameter is missing or has an invalid value.
    """
    pattern = router._view_name_mapping[view_name]
    segments = pattern.split('/')
    url_parts = []

    for segment in segments:
        dynamic_parts = re.findall(r'(<[^>]+>)', segment)
        for part in dynamic_parts:
            optional = '?' in part
            clean_part = part.replace('?', '').strip('<>')
            param_name_type = clean_part.split(':')
            param_name = param_name_type[0]
            param_type = (
                param_name_type[1] if len(param_name_type) > 1 else 'default'
            )
            param_value = kwargs.get(param_name)

            if param_value is None:
                if optional:
                    segment = segment.replace(part, '')
                else:
                    raise ValueError(f'Parameter {param_name} is required.')
            else:
                if param_type not in router._route_type_mapping:
                    raise ValueError(f'Invalid type {param_type}.')
                elif not router._route_type_mapping[param_type].validate(
                    param_value
                ):
                    raise ValueError(f'Invalid value for {param_name}.')
                converted_value = router._route_type_mapping[
                    param_type
                ].convert(param_value)
                segment = segment.replace(part, converted_value)

        segment = re.sub(r'-+', '-', segment).strip('-')

        if segment:
            url_parts.append(segment)

    return '/' + '/'.join(filter(None, url_parts))
