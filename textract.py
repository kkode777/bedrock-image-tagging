import os
from textractor import Textractor
from textractor.data.constants import TextractFeatures
import boto3
s3 = boto3.client('s3')
def main():
    extractor = Textractor(region_name="us-east-1")
    file_name="healthy_life_style_1.pdf"  #healthy_life_style_2.pdf,healthy_life_style_3.pdf

    bucket="kkode-s3-bucket"
    file_path="/genaiblog/docs/"
    upload_path="genaiblog/images"
    full_path=f"s3://{bucket}/{file_path}/{file_name}"
    print(full_path)

    print("Start Document Analysis")
    document = extractor.start_document_analysis(
        file_source="s3://kkode-s3-bucket/genaiblog/docs/healthy_life_style_2.pdf",
        features=[TextractFeatures.LAYOUT],
        s3_upload_path=f"s3://{bucket}/{upload_path}/",
        save_image=True
    )
    print("Extract images")
    for i, page in enumerate(document.pages):
        for j, figure in enumerate(page.page_layout.figures):
            bbox = figure.bbox
            width, height = page.image.size
            figure_image = page.image.crop((
                bbox.x * width,
                bbox.y * height,
                (bbox.x + bbox.width) * width,
                (bbox.y + bbox.height) * height
            ))
            image_name=f"{file_name}_page_{i+1}_figure_{j+1}.jpeg"
            print(image_name)
            local_save_path=f"tmp/{image_name}"
            figure_image.save(local_save_path)
            s3_upload_path=f"{upload_path}/{image_name}"
            print(f"Upload to S3 -{s3_upload_path}")
            s3.upload_file(local_save_path, bucket, s3_upload_path)

if __name__ == "__main__":
    main()
