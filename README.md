# DefectVision
Для запуска требуется сбилдить darknet:
git clone https://github.com/AlexeyAB/darknet
cd darknet
mkdir build_release
cd build_release
cmake ..
cmake --build . --target install --parallel 8

Скопировать все файлы проекта в директорию darknet

Скачать веса по ссылке:

Переместить по пути darknet/data

Установить зависимости из requirements.txt

Для запуска rtsp сервера:
git clone https://github.com/aler9/rtsp-simple-server.git
cd rtsp-simple-server
./rtsp-simple-server

Запустить main.py из директории darknet
python main.py <path to up.mp4> <path to down.mp4>