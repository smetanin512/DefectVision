# DefectVision
Для запуска требуется сбилдить darknet:
git clone https://github.com/AlexeyAB/darknet
cd darknet
mkdir build_release
cd build_release
cmake ..
cmake --build . --target install --parallel 8

Устано