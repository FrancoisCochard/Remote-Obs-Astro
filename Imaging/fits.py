# Generic includes
import os
import shutil
import subprocess
from warnings import warn

# Numerical/image stugg
import numpy as np
import skimage.io as io

# Astropy
from astropy.io import fits
from astropy.wcs import WCS
from astropy import units as u

# Local
from utils import error


def solve_field(fname, timeout=180, solve_opts=None, **kwargs):
    """ Plate solves an image.

    Args:
        fname(str, required):       Filename to solve in .fits extension.
        timeout(int, optional):     Timeout for the solve-field command,
                                    defaults to 60 seconds.
        solve_opts(list, optional): List of options for solve-field.
        verbose(bool, optional):    Show output, defaults to False.
    """
    verbose = kwargs.get('verbose', False)
    if verbose:
        print("Entering solve_field")

    solve_field_script = "{}/scripts/solve_field.sh".format(os.getcwd())

    if not os.path.exists(solve_field_script):  # pragma: no cover
        raise error.InvalidSystemCommand(
            "Can't find solve-field: {}".format(solve_field_script))

    # Add the options for solving the field
    if solve_opts is not None:
        options = solve_opts
    else:
        #'--no-fits2fits',
        options = [
            '--guess-scale',
            '--cpulimit', str(timeout),
            '--no-verify',
            '--crpix-center',
            '--match', 'none',
            '--corr', 'none',
            '--wcs', 'none',
            '--downsample', '1',
        ]
        #'-L', '1.55',
        #'-H', '1.7',
        #'-u', 'arcsecperpix'
        #]
        #--no-plots

        if kwargs.get('overwrite', True):
            options.append('--overwrite')
        if kwargs.get('skip_solved', True):
            options.append('--skip-solved')

        if 'ra' in kwargs:
            options.append('--ra')
            options.append(str(kwargs.get('ra')))
        if 'dec' in kwargs:
            options.append('--dec')
            options.append(str(kwargs.get('dec')))
        if 'radius' in kwargs:
            options.append('--radius')
            options.append(str(kwargs.get('radius')))

    cmd = [solve_field_script] + options + [fname]
    if verbose:
        print("Cmd:", cmd)

    try:
        proc = subprocess.Popen(cmd, universal_newlines=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as e:
        raise error.InvalidCommand(
            "Can't send command to solve_field.sh: {} \t {}".format(e, cmd))
    except ValueError as e:
        raise error.InvalidCommand(
            "Bad parameters to solve_field: {} \t {}".format(e, cmd))
    except Exception as e:
        raise error.PanError("Error on plate solving: {}".format(e))

    if verbose:
        print("Returning proc from solve_field")

    return proc


def get_solve_field(fname, replace=True, remove_extras=True, **kwargs):
    """Convenience function to wait for `solve_field` to finish.

    This function merely passes the `fname` of the image to be solved along to `solve_field`,
    which returns a subprocess.Popen object. This function then waits for that command
    to complete, populates a dictonary with the EXIF information and returns. This is often
    more useful than the raw `solve_field` function

    The solve-field program produces the file X.rdls which contains the RA,Dec positions of reference (known) stars.
    (Not all known stars, but those that appeared in the index files.)
    The X.corr file contains "correspondences" -- reference stars near stars detected in your image,
    with X,Y,RA,Dec positions. The X.axy file contains the pixel positions of sources detected in your image.
    You can use wcs-rd2xy and wcs-xy2rd programs to convert between X,Y and RA,Dec lists.

    <base>-ngc.png  : an annotation of the image.
    <base>.wcs      : a FITS WCS header for the solution.
    <base>.new      : a new FITS file containing the WCS header.
    <base>-objs.png : a plot of the sources (stars) we extracted from the image.
    <base>-indx.png : sources (red), plus stars from the index (green), plus the skymark (“quad”) used to solve the image.
    <base>-indx.xyls: a FITS BINTABLE with the pixel locations of stars from the index.
    <base>.rdls     : a FITS BINTABLE with the RA,Dec of sources we extracted from the image.
    <base>.axy      : a FITS BINTABLE of the sources we extracted, plus headers that describe the job (how the image is
                      going to be solved).
    <base>.solved   : exists and contains (binary) 1 if the field solved.
    <base>.match    : a FITS BINTABLE describing the quad match that solved the image.
    <base>.kmz      : (optional) KMZ file for Google Sky-in-Earth. You need to have “wcs2kml” in your PATH. See
                      http://code.google.com/p/wcs2kml/downloads/list
                      http://code.google.com/p/google-gflags/downloads/list

    Args:
        fname ({str}): Name of FITS file to be solved
        replace (bool, optional): Replace fname the solved file
        remove_extras (bool, optional): Remove the files generated by solver
        **kwargs ({dict}): Options to pass to `solve_field`

    Returns:
        dict: Keyword information from the solved field
    """
    verbose = kwargs.get('verbose', False)
    out_dict = {}
    output = None
    errs = None

    # Check for solved file
    if kwargs.get('skip_solved', True) and \
            (os.path.exists(fname.replace('.fits', '.solved')) or WCS(fname).is_celestial):
        if verbose:
            print(f"Solved file exists, skipping (pass skip_solved=False to solve again): {fname}")

        out_dict['solved_fits_file'] = fname
        return out_dict

    if verbose:
        print("Entering get_solve_field:", fname)

    # Set a default radius of 15
    kwargs.setdefault('radius', 15)
    #print("#############################################################################")
    #print(f"SOLVING {fname} with kwargs {kwargs}")
    #print("#############################################################################")
    proc = solve_field(fname, **kwargs)
    try:
        output, errs = proc.communicate(timeout=kwargs.get('timeout', 180))
    except subprocess.TimeoutExpired:
        proc.kill()
        raise error.AstrometrySolverError("Timeout while solving")
    if verbose:
        print("Returncode:", proc.returncode)
        print("Output:", output)
        print("Errors:", errs)
    if proc.returncode == 3:
        raise error.AstrometrySolverError(f"solve-field not found: {output}")
    if not os.path.exists(fname.replace('.fits', '.solved')):
        raise error.AstrometrySolverError(f"File not solved, output {output}, errors: {errs}")

    try:
        # Handle extra files created by astrometry.net
        new = fname.replace('.fits', '.new')
        rdls = fname.replace('.fits', '.rdls')
        axy = fname.replace('.fits', '.axy')
        xyls = fname.replace('.fits', '-indx.xyls')
        annotated = fname.replace('.fits', '-ngc.png')

        if replace and os.path.exists(new):
            # Remove converted fits
            os.remove(fname)
            # Rename solved fits to proper extension
            os.rename(new, fname)

            out_dict['solved_fits_file'] = fname
        else:
            out_dict['solved_fits_file'] = new

        if remove_extras:
            for f in [rdls, axy, xyls]:
                if os.path.exists(f):
                    os.remove(f)

        # Always save the solved fits and solved png at the root of the project
        try:
            if "config" in kwargs:
                latest_path = f"{kwargs['config']['directories']['images']}/latest_pointing.png"
                shutil.copyfile(annotated, latest_path)
                if kwargs.get("gen_hips", False):
                    # Manage creation of the HIPS
                    hips_dir = f"{kwargs['config']['directories']['images']}/HIPS"
                    gen_hips(hips_dir=hips_dir, fits_path=fname)
        except Exception as e:
            warn(f"Problem with extracting pretty pointing image: {e}")

    except Exception as e:
        warn(f"Cannot remove extra files: {e}")

    if errs is not None:
        warn(f"Error in solving: {errs}")
    else:
        try:
            out_dict.update(fits.getheader(fname))
        except OSError:
            if verbose:
                print(f"Can't read fits header for: {fname}")
    return out_dict


def get_wcsinfo(fits_fname, verbose=False):
    """Returns the WCS information for a FITS file.

    Uses the `wcsinfo` astrometry.net utility script to get the WCS information
    from a plate-solved file.

    Parameters
    ----------
    fits_fname : {str}
        Name of a FITS file that contains a WCS.
    verbose : {bool}, optional
        Verbose (the default is False)
    Returns
    -------
    dict
        Output as returned from `wcsinfo`
    """
    assert os.path.exists(fits_fname), warn(
        "No file exists at: {}".format(fits_fname))

    wcsinfo = shutil.which('wcsinfo')
    if wcsinfo is None:
        raise error.InvalidCommand('wcsinfo not found')

    run_cmd = [wcsinfo, fits_fname]

    if verbose:
        print("wcsinfo command: {}".format(run_cmd))

    proc = subprocess.Popen(run_cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, universal_newlines=True)
    try:
        output, errs = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:  # pragma: no cover
        proc.kill()
        output, errs = proc.communicate()

    unit_lookup = {
        'crpix0': u.pixel,
        'crpix1': u.pixel,
        'crval0': u.degree,
        'crval1': u.degree,
        'cd11': (u.deg / u.pixel),
        'cd12': (u.deg / u.pixel),
        'cd21': (u.deg / u.pixel),
        'cd22': (u.deg / u.pixel),
        'imagew': u.pixel,
        'imageh': u.pixel,
        'pixscale': (u.arcsec / u.pixel),
        'orientation': u.degree,
        'ra_center': u.degree,
        'dec_center': u.degree,
        'orientation_center': u.degree,
        'ra_center_h': u.hourangle,
        'ra_center_m': u.minute,
        'ra_center_s': u.second,
        'dec_center_d': u.degree,
        'dec_center_m': u.minute,
        'dec_center_s': u.second,
        'fieldarea': (u.degree * u.degree),
        'fieldw': u.degree,
        'fieldh': u.degree,
        'decmin': u.degree,
        'decmax': u.degree,
        'ramin': u.degree,
        'ramax': u.degree,
        'ra_min_merc': u.degree,
        'ra_max_merc': u.degree,
        'dec_min_merc': u.degree,
        'dec_max_merc': u.degree,
        'merc_diff': u.degree,
    }

    wcs_info = {}
    for line in output.split('\n'):
        try:
            k, v = line.split(' ')
            try:
                v = float(v)
            except Exception:
                pass

            wcs_info[k] = float(v) * unit_lookup.get(k, 1)
        except ValueError:
            pass
            # print("Error on line: {}".format(line))

    wcs_info['wcs_file'] = fits_fname

    return wcs_info


def fpack(fits_fname, unpack=False, verbose=False):
    """ Compress/Decompress a FITS file

    Uses `fpack` (or `funpack` if `unpack=True`) to compress a FITS file

    Parameters
    ----------
    fits_fname : {str}
        Name of a FITS file that contains a WCS.
    unpack : {bool}, optional
        file should decompressed instead of compressed (default is False)
    verbose : {bool}, optional
        Verbose (the default is False)
    Returns
    -------
    str
        Filename of compressed/decompressed file
    """
    assert os.path.exists(fits_fname), warn(
        "No file exists at: {}".format(fits_fname))

    if unpack:
        fpack = shutil.which('funpack')
        run_cmd = [fpack, '-D', fits_fname]
        out_file = fits_fname.replace('.fz', '')
    else:
        fpack = shutil.which('fpack')
        run_cmd = [fpack, '-D', '-Y', fits_fname]
        out_file = fits_fname.replace('.fits', '.fits.fz')

    try:
        assert fpack is not None
    except AssertionError:
        warn("fpack not found (try installing cfitsio). File has not been changed")
        return fits_fname

    if verbose:
        print("fpack command: {}".format(run_cmd))

    proc = subprocess.Popen(run_cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, universal_newlines=True)
    try:
        output, errs = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        output, errs = proc.communicate()

    return out_file


def write_fits(data, header, filename, logger, exposure_event=None):
    """
    Write FITS file to requested location
    """
    hdu = fits.PrimaryHDU(data, header=header)

    # Create directories if required.
    if os.path.dirname(filename):
        os.makedirs(os.path.dirname(filename), mode=0o775, exist_ok=True)

    try:
        hdu.writeto(filename)
    except OSError as err:
        logger.error('Error writing image to {}!'.format(filename))
        logger.error(err)
    else:
        logger.debug('Image written to {}'.format(filename))
    finally:
        if exposure_event is not None:
            exposure_event.set()

def update_thumbnail(file_path, latest_path):
    try:
        with fits.open(file_path, 'readonly') as f:
            hdu = f[0]
            io.imsave(latest_path, hdu.data.astype(np.uint8))
    except Exception as e:
        warn(f"Exception while trying to save thumbnail: {e}")

def gen_hips(hips_dir, fits_path):
    if os.path.exists(hips_dir):
        shutil.rmtree(hips_dir)
    os.makedirs(hips_dir)
    cmd = ["java", "-Xmx2g", "-jar", "scripts/Aladin.jar", "-hipsgen", "maxthread=20",
           f"in={fits_path}", f"out={hips_dir}", "creator_did=HiPSID"]
    try:
        warn(f"About to start java program to generate pointing image HIPS")
        subprocess.run(cmd)
    except Exception as e:
        warn(f"Exception while trying to generate HIPS with command {cmd}: {e}")



def update_headers(file_path, info):
    with fits.open(file_path, 'update') as f:
        hdu = f[0]
        hdu.header.set('IMAGEID', info.get('image_id', ''))
        hdu.header.set('SEQID', info.get('sequence_id', ''))
        hdu.header.set('FIELD', info.get('field_name', ''))
        hdu.header.set('RA-FIELD', info.get('field_ra', ''), 'Degrees')
        hdu.header.set('RA-MNT', info.get('ra_mnt', ''), 'Degrees')
        hdu.header.set('DEC-FIELD', info.get('field_dec', ''), 'Degrees')
        hdu.header.set('DEC-MNT', info.get('dec_mnt', ''), 'Degrees')
        hdu.header.set('EQUINOX', info.get('equinox', 2000.))  # Assume J2000
        hdu.header.set('AIRMASS', info.get('airmass', ''), 'Sec(z)')
        hdu.header.set('FILTER', info.get('filter', ''))
        hdu.header.set('LAT-OBS', info.get('latitude', ''), 'Degrees')
        hdu.header.set('LONG-OBS', info.get('longitude', ''), 'Degrees')
        hdu.header.set('ELEV-OBS', info.get('elevation', ''), 'Meters')
        hdu.header.set('MOONSEP', info.get('moon_separation', ''), 'Degrees')
        hdu.header.set('MOONFRAC', info.get('moon_fraction', ''))
        hdu.header.set('CREATOR', info.get('creator', ''), 'RemoteObservatory Software version')
        hdu.header.set('INSTRUME', info.get('camera_uid', ''), 'Camera ID')
        hdu.header.set('OBSERVER', info.get('observer', ''), 'Observer name')
        hdu.header.set('ORIGIN', info.get('origin', ''))
        hdu.header.set('RA-RATE', info.get('tracking_rate_ra', ''), 'RA Tracking Rate')
