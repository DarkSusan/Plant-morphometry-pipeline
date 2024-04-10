import cv2
import inquirer

questions = [
    inquirer.List('confirm', message="Are you happy with the coordinates?", choices=["yes", "no"], carousel=True)]


def select_coordinates(img):
    confirm = 'no'
    while confirm == 'no':
        ix, iy, drawing, finished_drawing = -1, -1, False, False
        coordinates = {}

        def draw_rectangle(event, x, y, flags, param):
            nonlocal ix, iy, drawing, img_resized, finished_drawing, coordinates
            if event == cv2.EVENT_LBUTTONDOWN:
                drawing = True
                ix, iy = x, y

            elif event == cv2.EVENT_MOUSEMOVE:
                if drawing:
                    # Check if the mouse is within the image boundaries
                    x = max(0, min(x, img_resized.shape[1] - 1))
                    y = max(0, min(y, img_resized.shape[0] - 1))

                    # Draw a rectangle while mouse is moving
                    img_copy = img_resized.copy()
                    cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 1)
                    cv2.imshow("image", img_copy)

            elif event == cv2.EVENT_LBUTTONUP:
                drawing = False
                # Check if the mouse is within the image boundaries
                x = max(0, min(x, img_resized.shape[1] - 1))
                y = max(0, min(y, img_resized.shape[0] - 1))

                # Draw final rectangle
                cv2.rectangle(img_resized, (ix, iy), (x, y), (0, 255, 0), 1)
                cv2.imshow("image", img_resized)
                # Print coordinates based on original image size
                x_value = round(min(ix, x) / scaling_factor)
                y_value = round(min(iy, y) / scaling_factor)
                width_value = round(abs(ix - x) / scaling_factor)
                height_value = round(abs(iy - y) / scaling_factor)
                print("Top left corner (x, y):", x_value, y_value)
                print("Width:", width_value)
                print("Height:", height_value)
                print("ix, iy, x, y:", ix, iy, x, y)
                print("scaling factor:", scaling_factor)
                coordinates = {
                    "x": x_value,
                    "y": y_value,
                    "width": width_value,
                    "height": height_value,
                }
                finished_drawing = True

        # Define the window name
        cv2.namedWindow("image", cv2.WINDOW_NORMAL)

        # Resize the window to desired dimensions
        window_width, window_height = 1000, 1000
        # cv2.resizeWindow("image", window_width, window_height)

        # Scale the image to fit within window
        img_height, img_width, _ = img.shape
        ratio = img_width / img_height
        scaling_factor = (
            window_height / img_height if ratio < 1 else window_width / img_width
        )
        scaled_height = round(scaling_factor * img_height)
        scaled_width = round(scaling_factor * img_width)
        img_resized = cv2.resize(img, (scaled_width, scaled_height))

        # Set mouse callback function
        cv2.setMouseCallback("image", draw_rectangle)

        # Display the image
        cv2.imshow("image", img_resized)

        while True:
            if cv2.waitKey(1) & 0xFF == 27:  # Escape key to exit
                cv2.destroyAllWindows()
                break
            if finished_drawing:
                cv2.destroyAllWindows()
                break

        cv2.destroyAllWindows()
        answers = inquirer.prompt(questions)
        confirm = answers['confirm']
    return coordinates
