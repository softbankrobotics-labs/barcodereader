cmake_minimum_required(VERSION 2.8)
project(BarcodeReader)

find_package(qibuild)
include_directories("./zbar" "./zbar-generated")


qi_create_lib( BarcodeReader 
    zbar/debug.h zbar/config.c 
    zbar/error.h zbar/error.c zbar/symbol.h zbar/symbol.c 
    zbar/image.h zbar/image.c zbar/convert.c 
    zbar/processor.c zbar/processor.h zbar/processor/lock.c 
    zbar/refcnt.h zbar/refcnt.c zbar/timer.h zbar/mutex.h 
    zbar/event.h zbar/thread.h 
    zbar/window.h zbar/window.c zbar/video.h zbar/video.c 
    zbar/img_scanner.h zbar/img_scanner.c zbar/scanner.c 
    zbar/decoder.h zbar/decoder.c
    
    zbar/decoder/ean.h zbar/decoder/ean.c
    
    zbar/processor/posix.h zbar/processor/posix.c
    
    zbar/video/null.c
    
    zbar/processor/null.c zbar/window/null.c
    
    python/zbarmodule.c python/zbarmodule.h 
    python/enum.c python/exception.c python/symbol.c python/symbolset.c 
    python/symboliter.c python/image.c 
    python/processor.c python/imagescanner.c python/decoder.c python/scanner.c
)

qi_use_lib(BarcodeReader PYTHON ALVISION QI OPENCV2_CORE OPENCV2_HIGHGUI)
