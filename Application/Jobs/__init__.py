from config_main import CUDA_GPU

import Application.Jobs.get_image
import Application.Jobs.pyramid_image
import Application.Jobs.edge_canny_cv2
import Application.Jobs.blur_image
import Application.Jobs.kernel_convolution
import Application.Jobs.thresholding_image
import Application.Jobs.edge_gradient_magnitude
import Application.Jobs.processing_image
import Application.Jobs.kernels
import Application.Jobs.edge_directional_magnitude
import Application.Jobs.thinning
import Application.Jobs.edge_second_order
import Application.Jobs.morphological_operations
import Application.Jobs.line_hough
import Application.Jobs.line_connectivity
import Application.Jobs.edge_shen_castan
import Application.Jobs.image_augmentation
import Application.Jobs.processing_multiple_images
import Application.Jobs.edge_edline
import Application.Jobs.feature_detection
import Application.Jobs.grey_comatrix
import Application.Jobs.image_cube
if CUDA_GPU:
    import Application.Jobs.u_net
    import Application.Jobs.semseg
