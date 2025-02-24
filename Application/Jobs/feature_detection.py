# noinspection PyPackageRequirements
from typing import Tuple

# Do not delete used indirectly
# noinspection PyUnresolvedReferences
from Application.Frame import transferJobPorts
from Application.Frame.global_variables import JobInitStateReturn
from Application.Frame.transferJobPorts import get_port_from_wave
from Utils.log_handler import log_error_to_console, log_to_console
from Application.Config.create_config import jobs_dict, create_dictionary_element
from config_main import PYRAMID_LEVEL, FILTERS
from Application.Config.util import transform_port_name_lvl, transform_port_size_lvl, job_name_create, get_module_name_from_file

from Application.Utils.misc import save_keypoint_to_array
import cv2


############################################################################################################################################
# Init functions
############################################################################################################################################


def init_func_sift() -> JobInitStateReturn:
    """
    Init function for sift algorithm
    :return: INIT or NOT_INIT state for the job
    """
    return JobInitStateReturn(True)

############################################################################################################################################
# Main functions
############################################################################################################################################

def main_func(param_list: list = None) -> bool:
    """
    Main function for SIFT calculation job.
    :param param_list: Param needed to respect the following list:
                       [input_port_name, input_port_wave, number_of_features, number_of_octaves, contrast_threshold, edge_threshold,
                        sigma_gaussian, port_name_mask, port_output_keypoints,  port_output_descriptors, port_output_img]
    :return: True if the job executed OK.
    """
    # noinspection PyPep8Naming
    PORT_IN_POS = 0
    # noinspection PyPep8Naming
    PORT_IN_WAVE = 1
    # noinspection PyPep8Naming
    PORT_IN_NR_FEATURES = 2
    # noinspection PyPep8Naming
    PORT_IN_NR_OCTAVE_LAYERS = 3
    # noinspection PyPep8Naming
    PORT_IN_CONTRAST_THR = 4
    # noinspection PyPep8Naming
    PORT_IN_EDGE_THR = 5
    # noinspection PyPep8Naming
    PORT_IN_SIGMA = 6
    # noinspection PyPep8Naming
    PORT_IN_MASK = 7
    # noinspection PyPep8Naming
    PORT_OUT_KEYPOINTS = 8
    # noinspection PyPep8Naming
    PORT_OUT_DESCRIPTORS = 9
    # noinspection PyPep8Naming
    PORT_OUT_IMG = 10

    # verify that the number of parameters are OK.
    if len(param_list) != 11:
        log_error_to_console("SIFT JOB MAIN FUNCTION PARAM NOK", str(len(param_list)))
        return False
    else:
        # get needed ports
        p_in = get_port_from_wave(name=param_list[PORT_IN_POS], wave_offset=param_list[PORT_IN_WAVE])
        # set mask port to input image if none
        if param_list[PORT_IN_MASK] is not None:
            p_in_mask = get_port_from_wave(name=param_list[PORT_IN_MASK], wave_offset=param_list[PORT_IN_WAVE])
        else:
            p_in_mask = get_port_from_wave(name=param_list[PORT_IN_POS], wave_offset=param_list[PORT_IN_WAVE])
        # get output port
        p_out_keypoints = get_port_from_wave(name=param_list[PORT_OUT_KEYPOINTS])
        p_out_des = get_port_from_wave(name=param_list[PORT_OUT_DESCRIPTORS])
        p_out_img = get_port_from_wave(name=param_list[PORT_OUT_IMG])

        # check if port's you want to use are valid
        if p_in.is_valid() is True:
            try:
                sift_obj = cv2.SIFT_create(nfeatures=param_list[PORT_IN_NR_FEATURES], nOctaveLayers=param_list[PORT_IN_NR_OCTAVE_LAYERS],
                                           contrastThreshold=param_list[PORT_IN_CONTRAST_THR], edgeThreshold=param_list[PORT_IN_EDGE_THR],
                                           sigma=param_list[PORT_IN_SIGMA])

                kp, des = sift_obj.detectAndCompute(image=p_in.arr.copy(), mask=p_in_mask.arr)
                # image of features
                tmp = cv2.drawKeypoints(image=p_in.arr.copy(), keypoints=kp, outImage=p_out_img.arr.copy())
                p_out_img.arr[:] = tmp[:]
                p_out_img.set_valid()
                # save KeyPoints to port
                for idx in range(min(len(des), param_list[PORT_IN_NR_FEATURES])):
                    p_out_des.arr[idx][:] = des[idx]
                p_out_des.set_valid()
                # save descriptors to port
                for t in range(min(len(kp), param_list[PORT_IN_NR_FEATURES])):
                    tmp = save_keypoint_to_array(kp[t])
                    p_out_keypoints.arr[t][:] = tmp
                p_out_keypoints.set_valid()

            except BaseException as error:
                log_error_to_console("SIFT JOB NOK: ", str(error))
                pass
        else:
            return False

        return True


############################################################################################################################################
# Job create functions
############################################################################################################################################


def do_sift_job(port_input_name: str,
                number_features: int = 512, number_octaves: int = 3, contrast_threshold: float = 0.04, edge_threshold: int = 10,
                gaussian_sigma: float = 1.6, mask_port_name: str = None,
                port_kp_output: str = None, port_des_output: str = None, port_img_output: str = None,
                level: PYRAMID_LEVEL = PYRAMID_LEVEL.LEVEL_0, wave_offset: int = 0) -> Tuple[str, str, str]:
    """
    The scale-invariant feature transform (SIFT) is a feature detection algorithm in computer vision to detect and describe local features
    in images.SIFT keypoints of objects are first extracted from a set of reference images[1] and stored in a database. An object is
    recognized in a new image by individually comparing each feature from the new image to this database and finding candidate matching
    features based on Euclidean distance of their feature vectors. From the full set of matches, subsets of keypoints that agree on the
    object and its location, scale, and orientation in the new image are identified to filter out good matches. The determination of
    consistent clusters is performed rapidly by using an efficient hash table implementation of the generalised Hough transform.
    Each cluster of 3 or more features that agree on an object and its pose is then subject to further detailed model verification and
    subsequently outliers are discarded. Finally the probability that a particular set of features indicates the presence of an object is
    computed, given the accuracy of fit and number of probable false matches. Object matches that pass all these tests can be identified
    as correct with high confidence
    https://www.cs.ubc.ca/~lowe/papers/iccv99.pdf
    :param port_input_name: name of input port
    :param number_features: number of features to save, they are ranked by score
    :param number_octaves: The number of layers in each octave.
    :param contrast_threshold: The contrast threshold used to filter out weak features in semi-uniform (low-contrast) regions.
                               The larger the threshold, the less features are produced by the detector.
    :param edge_threshold: The threshold used to filter out edge-like features. Note that the its meaning is different from the
                           contrastThreshold, i.e. the larger the edgeThreshold, the less features are filtered out.
    :param gaussian_sigma: The sigma of the Gaussian applied to the input image at the octave #0.
    :param mask_port_name: Masks for each input image specifying where to look for keypoints
    :param port_kp_output: Output port name for KeyPoints list
    :param port_des_output: Output port name for descriptor list
    :param port_img_output: Output port name for image
    :param level: pyramid level to calculate at
    :param wave_offset: port wave offset. If 0 it is in current wave.
    :return: output image port name
    """

    input_port_name = transform_port_name_lvl(name=port_input_name, lvl=level)

    if port_kp_output is None:
        port_kp_output = 'SIFT_KP_NF_{nf}_NO_{no}_CT_{ct}_ET_{et}_G_{g}_{INPUT}'.format(nf=number_features, no=number_octaves,
                                                                                        ct=contrast_threshold.__str__().replace('.', '_'),
                                                                                        et=edge_threshold, g=gaussian_sigma.__str__().replace('.', '_'),
                                                                                        INPUT=port_input_name)
        if mask_port_name is not None:
            port_kp_output += '_MASKED_BY_' + mask_port_name

    if port_des_output is None:
        port_des_output = 'SIFT_DES_NF_{nf}_NO_{no}_CT_{ct}_ET_{et}_G_{g}_{INPUT}'.format(nf=number_features, no=number_octaves,
                                                                                          ct=contrast_threshold.__str__().replace('.', '_'),
                                                                                          et=edge_threshold, g=gaussian_sigma.__str__().replace('.', '_'),
                                                                                          INPUT=port_input_name)
        if mask_port_name is not None:
            port_des_output += '_MASKED_BY_' + mask_port_name

    if port_img_output is None:
        port_img_output = 'SIFT_IMG_NF_{nf}_NO_{no}_CT_{ct}_ET_{et}_G_{g}_{INPUT}'.format(nf=number_features, no=number_octaves,
                                                                                          ct=contrast_threshold.__str__().replace('.', '_'),
                                                                                          et=edge_threshold, g=gaussian_sigma.__str__().replace('.', '_'),
                                                                                          INPUT=port_input_name)
        if mask_port_name is not None:
            port_img_output += '_MASKED_BY_' + mask_port_name

    port_kp_output_name = transform_port_name_lvl(name=port_kp_output, lvl=level)
    port_kp_output_name_size = '({nr_kp}, {size_kp})'.format(nr_kp=number_features, size_kp=7)

    port_des_output_name = transform_port_name_lvl(name=port_des_output, lvl=level)
    port_des_output_name_size = '({nr_kp}, 128)'.format(nr_kp=number_features)

    port_img_output_name = transform_port_name_lvl(name=port_img_output, lvl=level)
    port_img_output_name_size = transform_port_size_lvl(lvl=level, rgb=True)

    if mask_port_name is not None:
        mask_port_name = transform_port_name_lvl(name=mask_port_name, lvl=level)

    input_port_list = [input_port_name]

    main_func_list = [input_port_name, wave_offset, number_features, number_octaves, contrast_threshold, edge_threshold, gaussian_sigma,
                      mask_port_name, port_kp_output_name, port_des_output_name, port_img_output_name]

    output_port_list = [(port_kp_output_name, port_kp_output_name_size, 'H', False),
                        (port_des_output_name, port_des_output_name_size, 'H', False),
                        (port_img_output_name, port_img_output_name_size, 'B', True)]

    job_name = job_name_create(action='SIFT', input_list=input_port_list, wave_offset=[wave_offset], level=level)

    d = create_dictionary_element(job_module=get_module_name_from_file(__file__),
                                  job_name=job_name,
                                  input_ports=input_port_list,
                                  init_func_name='init_func_sift', init_func_param=None,
                                  main_func_name='main_func',
                                  main_func_param=main_func_list,
                                  output_ports=output_port_list)

    jobs_dict.append(d)

    return port_kp_output, port_des_output, port_img_output


if __name__ == "__main__":
    # If you want to run something stand-alone
    pass
