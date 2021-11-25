import os
import requests

url = "http://semantics.istc.cnr.it/fred/graph-image"
method = "POST"
headers = {
    "Content-type": "text/turtle",
    "Accept": "image/png"
}

turtle_dir = "../Datasets/Paragraph1_EuroParl/turtle"
png_dir = "../Datasets/Paragraph1_EuroParl/png"

for lang in os.listdir(turtle_dir):
    in_dir = os.path.join(turtle_dir,lang)
    if(os.path.isdir(in_dir)):
        out_dir = os.path.join(png_dir, lang)
        try:
            os.mkdir(out_dir)
        except FileExistsError:
            print(f"Directory {out_dir} already exists.")
    
        for filename_in in os.listdir(in_dir):
            file_in = os.path.join(in_dir, filename_in)
            filename_out = filename_in.replace('ttl', 'png')
            file_out = os.path.join(out_dir, filename_out)

            overwrite=False
            if os.path.isfile(file_out):
                print(f"{file_out} already exists. Overwrite? y/[n]")
                if input() == 'y':
                    overwrite=True
            if overwrite is not False:
                with open(file_in, mode='rb') as data:
                    req = requests.request(method=method,
                                            url=url,
                                            data=data,
                                            headers=headers)
                    with open(file_out, mode='wb') as out:
                        out.write(req.content)
