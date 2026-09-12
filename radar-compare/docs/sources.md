# Sources

The 209 URLs below are the primary sources behind this reference, grouped by source type. They are a
selection, not the whole corpus: the seventeen research files in `research/` cite 403 distinct URLs
between them, and each of those files ends with its own complete source list. Where a vendor supplied
many near-identical pages that only confirmed a price, a stock state or a part number, those are
collapsed into one entry with a count.

## Manufacturer datasheets and application notes

- ST single-zone ranging datasheets, the authority on range and ambient conditions: [VL53L0X](https://www.st.com/resource/en/datasheet/vl53l0x.pdf),
  [VL53L1X](https://www.pololu.com/file/0J1506/vl53l1x.pdf),
  [VL53L3CX](https://www.pololu.com/file/0J1765/vl53l3cx.pdf),
  [VL53L4CD](https://www.pololu.com/file/0J2060/vl53l4cd.pdf),
  [VL53L4CX](https://cdn-learn.adafruit.com/assets/assets/000/111/219/original/vl53l4cx.pdf),
  [VL6180X](https://www.pololu.com/file/0J961/VL6180X.pdf).
- ST multizone datasheets, source of the horizontal and vertical fields of view used here:
  [VL53L5CX](https://www.pololu.com/file/0J1878/vl53l5cx.pdf),
  [VL53L7CX](https://download.mikroe.com/documents/datasheets/VL53L7CX_datasheet.pdf),
  [VL53L8CX](https://a.pololu-files.com/file/0J2029/vl53l8cx.pdf),
  [VL53L8CH](https://download.mikroe.com/documents/datasheets/VL53L8CH_datasheet.pdf),
  [VL53L9CX](https://www.st.com/resource/en/datasheet/vl53l9cx.pdf).
- ST user manuals and cover-glass notes, for zone geometry, driver limits and window design:
  [UM2884 (VL53L5CX)](https://www.st.com/resource/en/user_manual/um2884-a-guide-to-using-the-vl53l5cx-multizone-timeofflight-ranging-sensor-with-wide-field-of-view-ultra-lite-driver-uld-stmicroelectronics.pdf),
  [UM3038 (VL53L7CX)](https://www.pololu.com/file/0J1993/um3038-a-guide-to-using-the-vl53l7cx-timeofflight-multizone-ranging-sensor-with-90-fov-stmicroelectronics.pdf),
  [AN5231](https://www.st.com/resource/en/application_note/an5231-cover-window-guidelines-for-the-vl53l1x-longdistance-ranging-timeofflight-sensor-stmicroelectronics.pdf),
  [AN5856](https://www.st.com/resource/en/application_note/an5856-guidelines-for-the-cover-glass-of-the-vl53l5cx-timeofflight-8x8-multizone-sensor-with-wide-field-of-view-stmicroelectronics.pdf).
- Spinning-LiDAR datasheets: Slamtec
  [LD108 A1M8 rev 2.1](https://cdn-shop.adafruit.com/product-files/4010/4010_datasheet.pdf),
  [LD108 A1M8 v2.2](http://bucket.download.slamtec.com/b90ae0a89feba3756bc5aaa0654c296dc76ba3ff/LD108_SLAMTEC_rplidar_datasheet_A1M8_v2.2_en.pdf),
  [RPLIDAR A1](https://bucket-download.slamtec.com/datasheet/RPLIDAR_A1_Datasheet.pdf),
  [RPLIDAR C1](https://bucket-download.slamtec.com/datasheet/RPLIDAR_C1_Datasheet.pdf),
  [LDROBOT LD06](https://www.inno-maker.com/wp-content/uploads/2020/11/LDROBOT_LD06_Datasheet.pdf),
  [Hokuyo URG-04LX](https://www.hokuyo-aut.jp/products/data.php?id=112).
- Single-point ranging datasheets:
  [Benewake TFmini](https://cdn-shop.adafruit.com/product-files/3978/3978_manual_SJ-PM-TFmini-T-01_A03ProductManual_EN.pdf),
  [Garmin LIDAR-Lite v3](https://static.garmin.com/pumac/LIDAR_Lite_v3_Operation_Manual_and_Technical_Specifications.pdf),
  [Sharp GP2Y0A21YK](https://global.sharp/products/device/lineup/data/pdf/datasheet/gp2y0a21yk_e.pdf),
  [Sharp GP2Y0A02YK](https://www.pololu.com/file/0J156/gp2y0a02yk_e.pdf),
  [MaxBotix LV-MaxSonar-EZ](https://www.fdi.ucm.es/profesor/mendias/TFE/recursos/PMOD/LV-MaxSonar-EZ_Datasheet.pdf),
  [Vishay VCNL4200](https://www.vishay.com/docs/84430/vcnl4200.pdf).
- ams-OSRAM multizone dToF and eye safety:
  [TMF8801](https://look.ams-osram.com/m/277d0c5095367cb7/original/TMF8801-DS000648.pdf),
  [TMF8806](https://look.ams-osram.com/m/6df9ed5e6992daaa/original/TMF8806-Time-of-flight-sensor.pdf),
  [TMF8828](https://cdn.sparkfun.com/assets/0/d/8/3/a/TMF8828_datasheet.pdf),
  [TMF8821 product page](https://ams-osram.com/products/sensors/direct-time-of-flight-sensors-dtof/ams-tmf8821-configurable-4x4-multi-zone-time-of-flight-sensor),
  [TMF8828 product page](https://ams-osram.com/products/sensors/direct-time-of-flight-sensors-dtof/ams-tmf8828-configurable-8x8-multi-zone-time-of-flight-sensor),
  [VCSEL eye-safety note](https://look.ams-osram.com/m/4cc7579d06a72fe/original/Eye-safety-with-ams-OSRAM-IR-VCSELs-safe-limits-measurements-and-use-of-integrated-safety-features.pdf).
- Thermal and infrared presence datasheets:
  [Panasonic Grid-EYE](https://cdn.sparkfun.com/assets/4/1/c/0/1/Grid-EYE_Datasheet.pdf),
  [Grid-EYE reference specification](https://cdn-learn.adafruit.com/assets/assets/000/043/261/original/Grid-EYE_SPECIFICATIONS%28Reference%29.pdf),
  [Panasonic AMG8833 product page](https://na.industrial.panasonic.com/products/sensors/sensors-automotive-industrial-applications/lineup/grid-eye-infrared-array-sensor/series/70496/model/72453),
  [Melexis MLX90640](https://www.melexis.com/-/media/files/documents/datasheets/mlx90640-datasheet-melexis.pdf),
  [ST STHS34PF80 datasheet DS13916](https://www.st.com/resource/en/datasheet/sths34pf80.pdf).
- Radar datasheets and notes, for presence, micro-motion and radome design:
  [DFRobot C4001 (SEN0609)](https://dfimg.dfrobot.com/wiki/20522/SEN0609_gravity-c4001-24ghz-mmwave-human-presence-detection-sensor_datasheet_V1.pdf),
  [Seeed MR60BHA2](https://files.seeedstudio.com/wiki/mmwave-for-xiao/mr60/datasheet/MR60BHA2_Breathing_and_Heartbeat_Module.pdf),
  [Seeed MR60FDA2](https://files.seeedstudio.com/wiki/mmwave-for-xiao/mr60/datasheet/MR60FDA2_Fall_Detection_Module_Datasheet.pdf),
  [Hi-Link HLK-LD2410 user manual V1.03](https://seengreat.com/upload/file/86/HLK+LD2410+Life+Presence+Sensor+Module+Manual+V1.03%28220629%29.pdf),
  [Hi-Link LD2410 vendor page](https://www.hlktech.net/index.php?id=988),
  [Hi-Link LD2450 vendor page](https://www.hlktech.net/index.php?id=1157),
  [Waveshare HMMD radome guide](https://files.waveshare.com/wiki/HMMD-mmWave-Sensor/HMMD-mmWave-Sensor%20Radome%20Design%20Guide%20.pdf),
  [Infineon AN003623](https://www.infineon.com/dgdl/Infineon-AN003623_Presence_detection_and_zoning_solution_using_XENSIV_BGT60TR13C_radar_and_CYW55913_Wi-Fi_Bluetooth_MCU-ApplicationNotes-v01_00-EN.pdf?fileId=8ac78c8c92416ca501925a36bfa408ad),
  [TI SWRA818, 60 GHz radar and false detections](https://www.ti.com/lit/an/swra818/swra818.pdf),
  [TI SWRA705, mmWave radar radome design guide](https://www.ti.com/lit/an/swra705/swra705.pdf),
  [TI TIDUCV3B, PIR signal-chain user guide](https://www.ti.com/lit/ug/tiducv3b/tiducv3b.pdf),
  [ADI 24 GHz FMCW primer](https://www.analog.com/en/resources/technical-articles/how-to-build-a-24-ghz-fmcw-radar-system.html),
  [RFbeam, understanding radar detection range](https://rfbeam.ch/understanding-detection-range-of-radar-sensors/).
- Bus and power parts for the ring wiring:
  [NXP P82B715](https://www.nxp.com/docs/en/data-sheet/P82B715.pdf),
  [NXP AN10710](https://www.nxp.com/docs/en/application-note/AN10710.pdf),
  [NXP SC16IS752](https://www.nxp.com/docs/en/data-sheet/SC16IS752_SC16IS762.pdf),
  [ADI LTC4311](https://www.analog.com/en/products/ltc4311.html).

## Vendor product and wiki pages

- Adafruit: forty-one product pages read for price, stock and breakout wiring, anchored on
  [4010 RPLIDAR A1](https://www.adafruit.com/product/4010),
  [4407 VL53L4CD](https://www.adafruit.com/product/4407),
  [3538 AMG8833](https://www.adafruit.com/product/3538) and
  [6426 STHS34PF80](https://www.adafruit.com/product/6426), plus the
  [time-of-flight](https://www.adafruit.com/search?q=time+of+flight) and
  [thermal camera](https://www.adafruit.com/search?q=thermal+camera) listings, read to confirm the
  catalogue was complete.
- Pololu and SparkFun:
  [ST ToF carriers](https://www.pololu.com/category/306/carriers-for-st-time-of-flight-tof-distance-sensors),
  [Qwiic VL53L5CX imager](https://www.sparkfun.com/sparkfun-qwiic-tof-imager-vl53l5cx.html),
  [Qwiic TCA9548A mux](https://www.sparkfun.com/sparkfun-qwiic-mux-breakout-8-channel-tca9548a.html),
  [Pimoroni VL53L5CX](https://shop.pimoroni.com/products/vl53l5cx-time-of-flight-tof-sensor-breakout).
- DFRobot wikis, the primary documentation for the mmWave parts:
  [SEN0395](https://wiki.dfrobot.com/sen0395/),
  [SEN0609](https://wiki.dfrobot.com/sen0609/),
  [SEN0610](https://wiki.dfrobot.com/SKU_SEN0610_Gravity_C4001_mmWave_Presence_Sensor_12m_I2C_UART),
  [SEN0623](https://wiki.dfrobot.com/sen0623/),
  [SEN0691 C4002](https://wiki.dfrobot.com/sen0691/),
  [SEN0557](https://wiki.dfrobot.com/sen0557/), with twenty-nine DFRobot store, blog and search pages
  for the 24, 60 and 77 GHz line-up and pricing.
- Scanner vendors: [Slamtec A1 parameters](https://www.slamtec.com/en/lidar/a1spec),
  [Slamtec C1](https://www.slamtec.com/en/c1),
  [Slamtec C1 datasheet mirror](https://static.generation-robots.com/media/slamtec-rplidar-c1-datasheet.pdf),
  [YDLIDAR triangulation range](https://www.ydlidar.com/product/category/triangulation/),
  [Waveshare D500](https://www.waveshare.com/wiki/D500_LiDAR_Kit),
  [Waveshare LD19](https://www.waveshare.com/wiki/DTOF_LIDAR_LD19),
  [Livox Mid-360](https://www.livoxtech.com/mid-360/specs),
  [Benewake TF-Luna](https://en.benewake.com/TFLuna/index.html).
- Parts with no retail breakout:
  [VL53L9CX](https://www.st.com/en/imaging-and-photonics-solutions/vl53l9cx.html),
  [VL53L4ED](https://www.st.com/en/imaging-and-photonics-solutions/vl53l4ed.html),
  [STEVAL-VL53L9 at DigiKey](https://www.digikey.com/en/products/detail/stmicroelectronics/STEVAL-VL53L9/29294599),
  [X-NUCLEO-53L8A1](https://www.digikey.com/en/products/result?keywords=X-NUCLEO-53L8A1).
- Other sensing vendors read for the discrimination chapter:
  [Seeed MR60BHA2](https://www.seeedstudio.com/MR60BHA2-60GHz-mmWave-Sensor-Breathing-and-Heartbeat-Module-p-5945.html),
  [Person Sensor at The Pi Hut (discontinued)](https://thepihut.com/products/person-sensor-by-useful-sensors),
  [Seeed YOLOv8 benchmarks on Pi 5 and the AI kit](https://wiki.seeedstudio.com/benchmark_on_rpi5_and_cm4_running_yolov8s_with_rpi_ai_kit/),
  [TDK ultrasonic time-of-flight line-up](https://product.tdk.com/en/products/sensor/ultrasonic/tof/index.html),
  [DSC LC-100-PI pet-immune PIR](https://www.dsc.com/alarm-security-products/LC-100-PI%20-%20PIR%20Detector%20with%20Pet%20Immunity/93),
  [Resideo IS335 pet-immune PIR](https://www.resideo.com/us/en/pro/products/security/wired-sensors/motion-sensors/is335-pet-immune-pir-detector-40-ft-x-56-ft-is335/),
  [Bosch Blue Line Gen2 installation guide](https://manualzz.com/doc/33892839/bosch-blue-line-gen2-isc-bpr2-wp12-motion-detector-instal).
- Adafruit learn guides, for wiring, addressing and driver behaviour:
  [RPLIDAR on Pi](https://learn.adafruit.com/slamtec-rplidar-on-pi),
  [AMG8833](https://learn.adafruit.com/adafruit-amg8833-8x8-thermal-camera-sensor/overview),
  [MLX90640](https://learn.adafruit.com/adafruit-mlx90640-ir-thermal-camera/overview),
  [STHS34PF80](https://learn.adafruit.com/adafruit-sths34pf80-ir-presence-motion-sensor),
  [TCA9548A](https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout/arduino-wiring-and-test),
  [I2C address list](https://learn.adafruit.com/i2c-addresses/the-list).

## Academic papers and standards

- Machine-safety standards, the basis of the stopping-distance and protective-field argument:
  [ISO 3691-4:2023 preview](https://cdn.standards.iteh.ai/samples/83545/a3d9d057a08d4f9c8e8e87cdc947583c/ISO-3691-4-2023.pdf),
  [ISO 13482](https://www.iso.org/standard/53820.html),
  [ANSI/A3 R15.08-2-2023](https://webstore.ansi.org/standards/ria/ansia3r15082023),
  [ANSI/RIA R15.08-1-2020](https://webstore.ansi.org/standards/ria/ansiriar15082020),
  [The Robot Report on R15.08](https://www.therobotreport.com/ansi-ria-r15-08-standard-redefines-industrial-mobile-robots-whats-new-and-why-it-matters/),
  [IEC 61496-1 explainer](https://www.pilz.com/en-US/iec-en-61496-1),
  [safety laser scanner and IEC 61496 guide](https://industrialsafetysensor.com/blog/safety-laser-scanners-guide/),
  [IEC 60825-1 laser-class summary](https://control.com/technical-articles/safety-considerations-for-lidar-sensors/),
  [EN 50636-2-107 (mowers)](https://standards.iteh.ai/catalog/standards/clc/3dff8f60-69c3-4a01-9a82-8770a8d0ecc8/en-50636-2-107-2015-a2-2020),
  [SICK ESPE white paper](https://www.sick.com/media/docs/7/57/057/whitepaper_electro_sensitive_protective_devices_espe_for_safe_machines_en_im0062057.pdf),
  [nanoScan3 product information](https://www.sick.com/media/docs/5/75/075/product_information_nanoscan3_en_im0087075.pdf),
  [Keyence SZ-V specifications](https://www.keyence.com/products/safety/laser-scanner/sz-v/specs/),
  [Banner AG4 application guide](https://info.bannerengineering.com/cs/groups/public/documents/literature/147900.pdf),
  [TUV Rheinland AGV white paper](https://www.tuv.com/content-media-files/master-content/services/industrial-services/pdf/tuv-rheinland-automatic-guided-vehicles-whitepaper-en_neu.pdf).
- Detection and classification literature, for what a 2D scan plane and a thermal array can separate:
  [leg detection from 2D range data](https://www.cs.mcgill.ca/~jpineau/files/leigh-icra15.pdf),
  [person detection in LiDAR (SPIE)](https://www.marcus-hebel.de/spie18_diehm_hammer_hebel_arens.pdf),
  [arXiv 1804.02463](https://arxiv.org/pdf/1804.02463),
  [arXiv 2106.11239](https://arxiv.org/pdf/2106.11239),
  [arXiv 2306.08531](https://arxiv.org/pdf/2306.08531),
  [arXiv 2408.01951](https://arxiv.org/abs/2408.01951),
  [ACM IMWUT 3610902, multi-person mmWave tracking](https://dl.acm.org/doi/10.1145/3610902),
  [EURASIP radar human sensing](https://asp-eurasipjournals.springeropen.com/articles/10.1186/s13634-021-00738-2),
  [Caroleo et al., VL53L5CX characterisation, Sensors 26(5):1639](https://www.mdpi.com/1424-8220/26/5/1639)
  ([full text, PMC12986679](https://pmc.ncbi.nlm.nih.gov/articles/PMC12986679/)),
  [Expert Systems with Applications 2018, DOI 10.1016/j.eswa.2018.02.019](https://doi.org/10.1016/j.eswa.2018.02.019),
  [RayPet, Springer 2024](https://link.springer.com/chapter/10.1007/978-981-97-3289-0_25),
  [MIRaSeg, Springer](https://link.springer.com/chapter/10.1007/978-981-95-5764-6_2),
  [UCT MSc, FMCW micro-Doppler](https://open.uct.ac.za/items/a65e9cb0-dbae-4a9d-a830-5a1177c08b90),
  [JRC78619, pedestrian radar cross section at 24 and 77 GHz](https://publications.jrc.ec.europa.eu/repository/handle/JRC78619),
  [UWB MIMO detection of stationary humans, PMC5134581](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5134581/),
  [Johnson criteria history, OSTI](https://www.osti.gov/servlets/purl/1222446).
- Physiology and animal-safety sources behind the pet and micro-motion claims:
  [PMC6888617](https://pmc.ncbi.nlm.nih.gov/articles/PMC6888617/),
  [PMC7070589](https://pmc.ncbi.nlm.nih.gov/articles/PMC7070589/),
  [PMC8944468](https://pmc.ncbi.nlm.nih.gov/articles/PMC8944468/),
  [PMC10497125](https://pmc.ncbi.nlm.nih.gov/articles/PMC10497125/),
  [PMC10777904](https://pmc.ncbi.nlm.nih.gov/articles/PMC10777904/),
  [PMC12158235](https://pmc.ncbi.nlm.nih.gov/articles/PMC12158235/),
  [Border collie and labrador gait, PMC4687030](https://pmc.ncbi.nlm.nih.gov/articles/PMC4687030/),
  [canine gait parameters, PMC5015230](https://pmc.ncbi.nlm.nih.gov/articles/PMC5015230/),
  [walk-to-run transition stride frequency, PMC5435734](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5435734/),
  [forehead versus core temperature, PMC9740153](https://pmc.ncbi.nlm.nih.gov/articles/PMC9740153/),
  [torso skin temperature under clothing, PubMed 3349991](https://pubmed.ncbi.nlm.nih.gov/3349991/),
  [Sensors 2024 24(6):1901, PMC10975529](https://pmc.ncbi.nlm.nih.gov/articles/PMC10975529/),
  [PDSA resting respiratory rate](https://www.pdsa.org.uk/pet-help-and-advice/pet-health-hub/other-veterinary-advice/how-to-record-a-resting-respiratory-rate),
  [Oxford hedgehog mower safety test](https://www.ox.ac.uk/news/2024-01-16-researchers-develop-hedgehog-safety-test-robotic-lawnmowers).
- Materials, optics and building geometry:
  [PLA permittivity at mm-wave](https://www.researchgate.net/publication/313543263_Complex_permittivity_and_anisotropy_measurement_of_3D-printed_PLA_at_microwaves_and_millimeter-waves),
  [germanium LWIR windows](https://www.edmundoptics.com/f/germanium-ge-windows/13137/),
  [germanium lenses and LWIR optics](https://workswell.eu/germanium-lens-lwir-optics-thermal-cameras-modules/),
  [what long-wave infrared imaging is](https://www.lightpath.com/insights/what-is-long-wave-infrared-imaging-and-where-is-it-used),
  [2018 IRC stair geometry](https://inspectapedia.com/Stairs/2018-IRC-Stair-Code-CO.pdf),
  [Boise tread and riser sheet](https://www.cityofboise.org/media/14405/437-treads-risers_march-2022.pdf),
  [US10594920B2 (cliff detection patent)](https://patents.google.com/patent/US10594920B2/en).

## Community and teardown sources

- Teardowns and platform documentation, for prior-art sensor placement and ring height:
  [iFixit Amazon Astro teardown](https://www.ifixit.com/News/70384/amazon-astro-teardown),
  [iRobot Create 3 hazards API](https://iroboteducation.github.io/create3_docs/api/hazards/),
  [Create 3 URDF](https://github.com/iRobotEducation/create3_sim/blob/b7c69013d0db241df64199cae9491286635d1bcc/irobot_create_common/irobot_create_description/urdf/create3.urdf.xacro),
  [TurtleBot 4 sensors](https://turtlebot.github.io/turtlebot4-user-manual/software/sensors.html),
  [TurtleBot 4 overview brochure](https://www.generationrobots.com/media/turtlebot4/Turtlebot_4_OverviewBrochure.pdf),
  [Anki Vector technical reference](https://randym32.github.io/Vector-TRM.pdf),
  [Anki Vector SDK proximity sensor](https://vector.ikkez.de/generated/anki_vector.proximity.html),
  [Starship robot specifications](https://www.wevolver.com/specs/starship-technologies-starship-robot).
- Shipping-platform vendor pages behind the prior-art chapter:
  [Starship our-robots](https://www.starship.xyz/our-robots/),
  [Kiwibot dimensions](https://www.dimensions.com/element/kiwibot),
  [Pudu BellaBot](https://www.pudurobotics.com/en/products/bellabot),
  [temi 3 service robot](https://www.generationrobots.com/en/404221-temi-3-service-robot.html),
  [iPresence on the mechanics of temi](https://ipresence.jp/en/magazine/temi-structure-robotics/),
  [Ohmni telepresence robot](https://ohmnilabs.com/products/ohmni-telepresence-robot/),
  [IEEE Spectrum on Double 3](https://spectrum.ieee.org/new-double-3-robot-makes-telepresence-easier-than-ever),
  [Amazon Astro (Wikipedia)](https://en.wikipedia.org/wiki/Amazon_Astro),
  [Roomba Max 705 retail listing](https://www.amazon.com/iRobot-Roomba-Robot-Vacuum-AutoEmpty/dp/B0DWG3C3ZF),
  [Roborock StarSight (US)](https://us.roborock.com/pages/roborock-starsight-autonomous-system),
  [Husqvarna Automower 435X AWD](https://www.husqvarna.com/us/robotic-lawn-mowers/automower-435x-awd/),
  [Husqvarna support KA-70110](https://us-support.husqvarna.com/en/automower/KA-70110),
  [Segway Navimow X3](https://navimow.com/pages/navimow-x3),
  [Navimow VisionFence](https://navimow.com/blogs/navimow-technology/visionfence-technology-the-vision-and-ai-driven-innovation-of-intelligent-mowing),
  [rbtx SICK nanoScan3 pricing](https://rbtx.com/en-US/components/safety/sick-safety-laser-scanners-nanoscan3).
- Driver source read directly when the datasheet was silent:
  [rplidar_sdk](https://github.com/Slamtec/rplidar_sdk),
  [rplidar_ros](https://github.com/Slamtec/rplidar_ros),
  [Adafruit CircuitPython RPLIDAR](https://github.com/adafruit/Adafruit_CircuitPython_RPLIDAR),
  [stm32duino VL53L1X class header](https://raw.githubusercontent.com/stm32duino/VL53L1X/main/src/vl53l1x_class.h),
  [stm32duino VL53L8CX API](https://raw.githubusercontent.com/stm32duino/VL53L8CX/main/src/vl53l8cx_api.h),
  [DFRobot_C4001](https://github.com/DFRobot/DFRobot_C4001),
  [DFRobot_C4002](https://github.com/DFRobot/DFRobot_C4002),
  [DFRobot_HumanDetection](https://github.com/DFRobot/DFRobot_HumanDetection),
  [ESPHome dfrobot_sen0395](https://esphome.io/components/dfrobot_sen0395/),
  [LD2410 field notes](https://www.sudo.is/docs/esphome/components/ld2410/),
  [ESP Easy P159 LD2410 plugin](https://espeasy.readthedocs.io/en/latest/Plugin/P159.html),
  [CircuitPython RPLIDAR docs](https://docs.circuitpython.org/projects/rplidar/en/latest/),
  [rplidar_ros on ROS Index](https://index.ros.org/p/rplidar_ros/),
  [HC-SR04 beam tests](https://github.com/GaryDyr/HC-SR04-beam-tests).
- Forum threads and applications notes on multi-sensor interference, cover windows and sunlight
  limits:
  [ST: multiple sensors interfering](https://community.st.com/t5/imaging-sensors/multiple-sensors-generate-interference-between-each-other/td-p/206535),
  [ST: VL53L5CX sunlight range](https://community.st.com/t5/imaging-sensors/vl53l5cx-sunlight-range/td-p/602218),
  [ST: VL53L7CH vs CX](https://community.st.com/t5/imaging-sensors/difference-between-the-vl53l7-ch-and-cx-variants/td-p/845353),
  [ST: cover-glass air gap](https://community.st.com/t5/imaging-sensors/vl53l5cx-gasket-requirements-with-cover-window-and-large-air-gap/td-p/142460),
  [Infineon BGT60TR13C FAQ](https://community.infineon.com/t5/Knowledge-Base-Articles/XENSIV-BGT60TR13C-radar-FAQs/ta-p/393702),
  [Adafruit forum 190482](https://forums.adafruit.com/viewtopic.php?f=22&t=190482),
  [Create 3 discussion 342](https://github.com/iRobotEducation/create3_docs/discussions/342),
  [PIR false-trigger troubleshooting](https://industrialmonitordirect.com/blogs/knowledgebase/pir-motion-sensor-false-triggers-industrial-application-troubleshooting),
  [multiple HC-SR04 crosstalk and interleave](https://industrialmonitordirect.com/blogs/knowledgebase/using-multiple-hc-sr04-ultrasonic-sensors-triangulation-setup-and-interference-prevention),
  [HC-SR04 tutorial](https://lastminuteengineers.com/arduino-sr04-ultrasonic-sensor-tutorial/),
  [pyroelectric and passive-infrared primer](https://www.electronicspecifier.com/products/sensors/motion-detection-using-pyro-electric-and-passive-infrared/),
  [thermal detection, recognition and identification explainer](https://kintronics.com/detection-recognition-and-identification-using-thermal-imaging-vs-optical-ip-camera/).
- Consumer-robot field reports and vendor claims, the evidence that dark, low-reflectance targets are
  the real field problem:
  [Vacuum Wars obstacle avoidance](https://vacuumwars.com/best-robot-vacuums-with-obstacle-avoidance/),
  [Samsung community: dark carpet cliff sensor](https://eu.community.samsung.com/t5/home-appliances/cliff-sensor-problem-where-the-vacuum-won-t-go-over-dark-carpets/td-p/12980487),
  [black rug avoidance](https://www.expertsinvacuum.com/why-your-robot-vacuum-wont-clean-black-rugs/),
  [dark-rug cliff-sensor insight](https://www.alibaba.com/product-insights/why-does-my-robot-vacuum-get-stuck-on-dark-rugs-and-how-to-trick-its-sensors.html),
  [Ecovacs pet-waste avoidance](https://www.ecovacs.com/us/blog/robot-vacuum-avoid-poop),
  [iRobot Pet Owner Official Promise](https://www.irobot.com/en_US/pet-promise.html),
  [Roborock StarSight](https://global.roborock.com/pages/roborock-starsight-autonomous-system),
  [TechCrunch on Astro pet detection](https://techcrunch.com/2022/09/28/amazon-astro-robot-pet-detection/),
  [GeekWire on Astro for Business](https://www.geekwire.com/2024/amazon-discontinues-astro-for-business-robot-security-guard-to-focus-on-astro-home-robot/).
- Trade press and vendor announcements for parts with no datasheet-grade page yet:
  [CNX Software on VL53L9CX](https://www.cnx-software.com/2026/06/22/st-vl53l9cx-direct-time-of-flight-3d-lidar-supports-5cm-to-9m-range-2-3k-zones-resolution/),
  [ST newsroom p4783](https://newsroom.st.com/media-center/press-item.html/p4783.html),
  [Adafruit blog on the ams-OSRAM TMF8828](https://blog.adafruit.com/2024/08/27/tms8828-multi-zone-time-of-flight-sensor-from-ams-osram/).

## Method and limits of this source set

All research was carried out on 2026-09-12, and every file in `research/` carries that date. Sixteen
lanes ran as parallel web-research agents, one per subject area, and a seventeenth file,
`research/recommendation.md`, synthesised them. Numeric claims were then re-checked by an independent
adversarial pass that re-read the primary document and was told to look for errors, not to confirm
the finding. That pass is why several figures in the research files carry a correction note, including
the diagonal-field-of-view error described in `research/coverage-geometry.md`, which the coverage
chapter of this reference then uses.

Three limits apply. First, that adversarial pass is declared in sixteen of the seventeen files.
`research/dfrobot-mmwave-full-grid.md` is the exception: it marks each row with its own confidence
level but records no separate second pass, so its catalogue rows rest on a single reading of the
vendor page or wiki.

Second, every price and stock state is a single read on 2026-09-12 and nothing was re-read later, so
those figures age faster than the specifications beside them.

Third, **no part in this reference was purchased, bench-tested or physically measured by this
project.** Every figure is marked in its source lane as `datasheet-verified`, `vendor-page-verified`,
`standard-verified`, `peer-reviewed-measured`, `inferred` or `unverified`, and any measured number is
somebody else's measurement, not ours. The dark-target and sunlight figures are the ones most worth
confirming on the bench before a ring is committed to hardware, because those are exactly the
conditions the datasheets leave open: Slamtec states only "White objects" against the A1M8 range and
publishes no reflectivity percentage, and ST characterises the grid time-of-flight family at 0 and
5 kLux only, while direct sunlight is 100 to 120 kLux and ST publishes no figure for it. That reading
is an inference from those two gaps, not a measurement.
