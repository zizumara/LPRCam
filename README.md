# LPRCam
![Installed Camera](installed1.jpg)

This project includes the software and hardware design for a DIY motion-activated Raspberry Pi security camera.  The Linux Motion application is used to detect motion and capture images.  The following hardware is used for this project:
* Raspberry Pi Zero W
* Arducam 12.3 MP HQ camera with automatic IR-cut filter (www.arducam.com)
* Arducam 12mm CS-Mount Lens with Manual Focus and Adjustable Aperture (Amazon)
* A custom IR illuminator (KiCAD files included)
* A custom ambient light sensor (KiCAD files included)
* A 3D-printable enclosure (STL files included)
* A 5V 2.5A step-down voltage regulator (Pololu #2858)
* 2.1mm DC panel mount barrel jack (Adafruit #610)
* CESFONJER Mini Locking Toggle Switch (Amazon)
* GIVERARE Combination Travel Cable Lock (Amazon)
* DEWENWILS 60W Outdoor Low Voltage Transformer (Amazon)
* Woods 55213143 16/2 Low Voltage Lighting Cable, 100-Feet (Amazon)

For nighttime operation, when the ambient light sensor registers light below a configured level, software enables the IR illuminator and switches in the IR-cut filter on the camera module.

![Camera Box Interior](front-open-annotated.jpg)
