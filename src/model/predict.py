import torch


def predict_image(model, image):
    try:
        saved_model = torch.hub.load('mkang315/RCS-YOLO', 'custom', path_or_model=model)
        output_image = saved_model(image)  # Call your model's predict function
        output_image.print()
        print(output_image.pandas().xyxy[0])
        output_image.save()
        return output_image  # Example for results page
    except Exception as e:
        print(e)
