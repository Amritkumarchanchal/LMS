def add_x_tag_groups(result, generator, request, public):
    """
    Add x-tagGroups to the OpenAPI schema.

    Args:
        result (dict): The OpenAPI schema.
        generator (BaseSchemaGenerator): The schema generator instance.
        request (Request): The current request.
        public (bool): Whether the schema is public or private.

    Returns:
        dict: The modified schema.
    """
    result["x-tagGroups"] = [

        {
            "name": "Authentication",
            "tags":["Auth"]
        },
        {
            "name": "Courses",
            "tags": ["Course", "Course Instance", "Module", "Section"],
        },
        {
            "name": "Assessments",
            "tags": ["Assessment", "Question", "Solution"],
        },
        {
            "name": "Section Items",
            "tags": ["Item", "Video", "Article"],
        },
        {
            "name": "Institution",
            "tags": ["Institution"],
        },
        {
            "name": "User",
            "tags": ["Users", "User Institutions", "User Courses"],
        }



    ]
    return result