# -----------------------------------------------
# Get Canonical Coordinates from CrowdCafe data
# -----------------------------------------------
def getRectangleCoordinates(shape):
    # convert rectangle into polygon to have the same logic for both shape types
    return [
        {'x': shape['left'], 'y': shape['top']},  # left - top
        {'x': shape['left'] + shape['width'] * shape['scaleX'], 'y': shape['top']},  # right - top
        {'x': shape['left'] + shape['width'] * shape['scaleX'], 'y': shape['top'] + shape['height'] * shape['scaleY']},
        # right - bottom
        {'x': shape['left'], 'y': shape['top'] + shape['height'] * shape['scaleY']}  # left - bottom
    ]

def getPolygonPoints(shape):
    # apply starting point shift to all points of the polygon
    return [{'x': point['x'] + shape['left'], 'y': point['y'] + shape['top']} for point in shape['points']]


def getCanvasSize(shape):
    canvas = {}
    for key in ['width', 'height']:
        canvas[key] = shape[key]
    return canvas