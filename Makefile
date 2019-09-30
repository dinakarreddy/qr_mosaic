IMAGE_NAME=qr

run: build
	#@command docker run --rm -it -v $(shell pwd)/src:/qr $(IMAGE_NAME) python single_qr_image.py
	#@command docker run --rm -it -v $(shell pwd)/src:/qr $(IMAGE_NAME) python multi_qr_image.py
	#@command docker run --rm -it -v $(shell pwd)/src:/qr $(IMAGE_NAME) python qr.py --final_img_type=pencil
	#@command docker run --rm -it -v $(shell pwd)/src:/qr $(IMAGE_NAME) python mosaic.py
	@command docker run --rm -it -v $(shell pwd)/src:/qr $(IMAGE_NAME) python mosaic_best_fit.py
	#python mosaic_best_fit.py --target_img_file_path=images/1.jpeg --final_img_file_path=images/result_images/mosaic_best_fit.jpeg

build: check-pre-requisites
	@command docker build -t $(IMAGE_NAME) ./

check-pre-requisites:
	@command -v docker || (echo "Docker not installed!" && exit 1)
	@command -v docker-compose || (echo "Docker compose not installed!" && exit 1)
