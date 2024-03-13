import argparse, sys, os, itertools, difflib, json, re, mimetypes, traceback
from skimage.transform import rotate
from deskew import determine_skew
from pdf2image import convert_from_path, convert_from_bytes
import nltk, numpy, textract, cv2, pytesseract
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.corpus import stopwords
from django.conf import settings
from PIL import Image
from io import BytesIO
from docx import Document
import multiprocessing

class Octopii:

    def set_regexes(self):
        with open(f"{settings.BASE_DIR}/utils/handlers/definitions.json", "r", encoding='utf-8') as json_file:
            self.regex_rules = json.load(json_file)
    
    def set_handlers(self):
        self.handlers = {
            '.csv': self.plan_text_handler,
            # '.doc': self.plan_text_handler,
            '.docx': self.plan_text_handler,
            # '.eml': self.plan_text_handler,
            # '.epub': self.plan_text_handler,
            '.htm': self.plan_text_handler,
            '.html': self.plan_text_handler,
            '.json': self.plan_text_handler,
            # '.odt': self.plan_text_handler,
            # '.pptx': self.plan_text_handler,
            # '.ps': self.plan_text_handler,
            # '.rtf': self.plan_text_handler,
            # '.tsv': self.plan_text_handler,
            '.txt': self.plan_text_handler,
            # '.xls': self.plan_text_handler,
            # '.xlsx': self.plan_text_handler,
            '.pdf': self.pdf_handler,
            # '.mp3': self.audio_handler,
            # '.ogg': self.audio_handler,
            # '.wav': self.audio_handler,
            # '.gif': self.image_handler,
            '.jpeg': self.image_handler,
            '.jpg': self.image_handler,
            '.png': self.image_handler,
            '.webp': self.image_handler,
            # '.tif': self.image_handler,
            '.tiff': self.image_handler
        }

    def __init__(self, file):
        self.file = file
        self.set_handlers()
        self.set_regexes()

        # if os.path.isdir(self.file):
        #     raise Exception(f"{self.file} is a directory and directory are not allowed in current version")

        # if not os.path.exists(self.file):
        #     raise FileNotFoundError(f"The file '{self.file}' does not exist.")
        
        self.mime_type, encoding = mimetypes.guess_type(self.file.name)
        if not self.mime_type:
            self.file_extension = f".{self.file.name.split('.', -1)[-1]}"
        else:
            self.file_extension = mimetypes.guess_extension(self.mime_type)
        
        if self.file_extension.lower() not in self.handlers.keys():
            raise Exception(f"File extension {self.file_extension} is not allowed")
    
    def scan_image_for_people(self, image):
        image = numpy.array(image)
        cascade_values_file = f"{settings.BASE_DIR}/utils/handlers/face_cascade.xml"
        cascade_values = cv2.CascadeClassifier(cascade_values_file)
        faces = cascade_values.detectMultiScale (
            image,
            scaleFactor = 1.1,
            minNeighbors = 5,
            minSize = (30, 30),
            flags = cv2.CASCADE_SCALE_IMAGE
        )
        return len(faces)
    

    def scan_image_for_text(self,image):
        image = numpy.array(image) # converts the image to a compatible format

        # 0. Original 
        try:
            image_text_unmodified = pytesseract.image_to_string(image, config = '--psm 12')
        except TypeError:
            print("Cannot open this file type.")
            return
        #cv2.imwrite("image0.png", image)

        # 1. Auto-rotation
        try: 
            print ("Attempting to auto-rotate image and read text")
            try:
                degrees_to_rotate = pytesseract.image_to_osd(image)
            except: degrees_to_rotate = "Rotate: 180"

            for item in degrees_to_rotate.split("\n"):
                if "rotate".lower() in item.lower():
                    degrees_to_rotate = int(item.replace(" ", "").split(":", 1)[1])
                    if degrees_to_rotate == 180:
                        pass
                    elif degrees_to_rotate == 270:
                        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    elif degrees_to_rotate == 360:
                        image = cv2.rotate(image, cv2.ROTATE_180)

            image_text_auto_rotate = pytesseract.image_to_string(image, config = '--psm 12')
            #cv2.imwrite("image1.png", image)
        except: 
            print ("Couldn't auto-rotate image")
            image_text_auto_rotate = ""

        # 2. Grayscaled
        try: 
            print ("Reading text from grayscaled image")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            image_text_grayscaled = pytesseract.image_to_string(image, config = '--psm 12')
            #cv2.imwrite("image2.png", image)
        except: 
            print ("Couldn't grayscale image")
            image_text_grayscaled = ""

        # 3. Monochromed
        try: 
            print ("Reading text from monochromed image")
            image = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            image_text_monochromed = pytesseract.image_to_string(image, config = '--psm 12')
            #cv2.imwrite("image3.png", image)
        except: 
            print ("Couldn't monochrome image")
            image_text_monochromed = ""

        # 4. Mean threshold
        try:
            print ("Reading text from mean threshold image")
            image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
            image_text_mean_threshold = pytesseract.image_to_string(image, config = '--psm 12')
            #cv2.imwrite("image4.png", image)
        except: 
            print ("Couldn't mean threshold image")
            image_text_mean_threshold = ""

        # 5. Gaussian threshold
        try:
            print ("Reading text from gaussian threshold image")
            image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 11, 2)
            image_text_gaussian_threshold = pytesseract.image_to_string(image, config = '--psm 12')
            #cv2.imwrite("image5.png", image)
        except: 
            print ("Couldn't gaussian threshold image")
            image_text_gaussian_threshold = ""

        # 6. Deskew
        try:
            # 6a. Deskew one
            print ("First attempt at de-skewing image and reading text")
            angle = determine_skew(image)
            rotated = rotate(image, angle, resize=True) * 255
            image = rotated.astype(numpy.uint8)
            image_text_deskewed_1 = pytesseract.image_to_string(image, config = '--psm 12')
            #cv2.imwrite("image6.png", image)

            # 6b. Deskew two
            print ("Second attempt at de-skewing image and reading text")
            angle = determine_skew(image)
            rotated = rotate(image, angle, resize=True) * 255
            image = rotated.astype(numpy.uint8)
            image_text_deskewed_2 = pytesseract.image_to_string(image, config = '--psm 12')
            #cv2.imwrite("image7.png", image)

            # 6c. Deskew three
            print ("Third attempt at de-skewing image and reading text")
            angle = determine_skew(image)
            rotated = rotate(image, angle, resize=True) * 255
            image = rotated.astype(numpy.uint8)
            image_text_deskewed_3 = pytesseract.image_to_string(image, config = '--psm 12')
            #cv2.imwrite("image8.png", image)
        except: 
            print ("Couldn't deskew image")
            image_text_deskewed_1 = ""
            image_text_deskewed_2 = ""
            image_text_deskewed_3 = ""

        # END OF IMAGE PROCESSING AND OCR

        # Tokenize all scanned strings by newlines and spaces
        unmodified_words = self.string_tokenizer(image_text_unmodified)
        grayscaled = self.string_tokenizer(image_text_grayscaled)
        auto_rotate = self.string_tokenizer(image_text_auto_rotate)
        monochromed = self.string_tokenizer(image_text_monochromed)
        mean_threshold = self.string_tokenizer(image_text_mean_threshold)
        gaussian_threshold = self.string_tokenizer(image_text_gaussian_threshold)
        deskewed_1 = self.string_tokenizer(image_text_deskewed_1)
        deskewed_2 = self.string_tokenizer(image_text_deskewed_2)
        deskewed_3 = self.string_tokenizer(image_text_deskewed_3)

        original = image_text_unmodified + "\n" + image_text_auto_rotate + "\n" + image_text_grayscaled + "\n" + image_text_monochromed + "\n" + image_text_mean_threshold + "\n" + image_text_gaussian_threshold + "\n" + image_text_deskewed_1 + "\n" + image_text_deskewed_2 + "\n" +  image_text_deskewed_3

        intelligible = unmodified_words + grayscaled + auto_rotate + monochromed + mean_threshold + gaussian_threshold + deskewed_1 + deskewed_2 + deskewed_3
        return (original, intelligible)


    def string_tokenizer(self,text):
        return text.replace(" ","\n").split("\n")
    
    def word_similarity_ratio(self, word_a, word_b):
        return difflib.SequenceMatcher(None, word_a, word_b).ratio() * 100

    def address_pii(self, text):
        resources = ["punkt", "maxent_ne_chunker", "stopwords", "words", "averaged_perceptron_tagger"]

        try:
            nltk_resources = ["tokenizers/punkt", "chunkers/maxent_ne_chunker", "corpora/words.zip"]
            for resource in nltk_resources:
                if not nltk.data.find(resource):
                    raise LookupError()
        except LookupError:
            for resource in resources:
                nltk.download(resource)

        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)
        tagged_words = pos_tag(words)
        named_entities = ne_chunk(tagged_words)

        locations = []

        for entity in named_entities:
            if isinstance(entity, nltk.tree.Tree):
                if entity.label() in ['GPE', 'GSP', 'LOCATION', 'FACILITY']:
                    location_name = ' '.join([word for word, tag in entity.leaves() if word.lower() not in stop_words and len(word) > 2])
                    locations.append(location_name)

        return list(set(locations))
    

    def email_pii(self, text):
        return list(set(re.findall(self.regex_rules['Email']['regex'], text)))
    
    def phone_number_pii(self, text):
        return list(set(re.findall(self.regex_rules['Phone Number']['regex'], text)))

    def identifiers_pii(self,text):
        results = []
        for key in self.regex_rules.keys():
            region = self.regex_rules[key]["region"]
            rule = self.regex_rules[key]["regex"]
            if region is not None:
                try:
                    match = re.findall(rule, text)
                except:
                    match=[]
                if len(match) > 0:
                    result = {'identifier_class':key, 'result': list(set(match))}
                    results.append(result)
        
        if len(results) != 0:
            results = results[0]["result"]
        return results

    def keywords_classify_pii(self, text):
        """
        The function `keywords_classify_pii` classifies text data based on keywords and returns the PII
        class, score, and country of origin.
        
        :param text: It looks like you have provided a code snippet for a function that classifies
        personally identifiable information (PII) based on keywords in a given text. However, you have
        not provided the actual text input for the function to process. If you provide the text input, I
        can help you test the function
        :return: The function `keywords_classify_pii` returns a dictionary containing the following keys
        and values:
        - "pii_class": the highest scoring PII class based on the keywords found in the input text
        - "score": the score associated with the highest scoring PII class
        - "country_of_origin": the region associated with the highest scoring PII class
        """
        intelligible_text_list = self.string_tokenizer(text)
        keywords_scores = {}
        
        for key, rule in self.regex_rules.items():
            keywords_scores[key] = 0
            keywords = rule.get("keywords", [])
            if keywords is not None:
                for intelligible_text_word in intelligible_text_list:
                    for keywords_word in keywords:
                        if self.word_similarity_ratio(
                            intelligible_text_word.lower()
                                .replace(".", "")
                                .replace("'", "")
                                .replace("-", "")
                                .replace("_", "")
                                .replace(",", ""),
                            keywords_word.lower()
                        ) > 80: keywords_scores[key] += 1
        
        pii_class, score = max(keywords_scores.items(), key=lambda x: x[1])
        country_of_origin = self.regex_rules[pii_class]["region"]
        result = {
            "pii_class": pii_class if pii_class else "",
            "score": score if score else 0,
            "country_of_origin": country_of_origin if country_of_origin else ""
        }

        return result

    def search_pii(self, text, contains_faces=0):
        emails = self.email_pii(text)
        phone_numbers = self.phone_number_pii(text)
        addresses = self.address_pii(text)
        identifiers = self.identifiers_pii(text)
        keywords_classify_result = self.keywords_classify_pii(text)
        return {**{
            'emails':emails,
            'contains_faces': contains_faces,
            'phone_numbers': phone_numbers,
            'addresses': addresses,
            'identifiers': identifiers,
            'origin': 'Local',
            'file_extension': self.file_extension,
            'owner':'admin',
            'name_of_file': self.file.name,
            'is_file':True,
            'file_location':'temp'
        },
        **keywords_classify_result
        }

    def docx_parser(self):
        file_stream = BytesIO(self.file.read())
        document = Document(file_stream)
        text = []
        for paragraph in document.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    
    def plan_text_handler(self):
        if self.file_extension in [".txt", ".json", ".csv", ".html", ".htm"]:
            text = self.file.read().decode()
        elif self.file_extension in [".docx"]:
            text = self.docx_parser()
        else:
            text = textract.process(self.file).decode()
        return self.search_pii(text)
    
    def image_handler(self):
        # image = cv2.imread(self.file)
        image = Image.open(self.file)
        # image = numpy.array(image)
        contains_faces = self.scan_image_for_people(image)
        text, intelligible = self.scan_image_for_text(image)
        return self.search_pii(text, contains_faces)

    def pdf_handler(self):
        # images = convert_from_path(self.file)
        images = convert_from_bytes(self.file.read())
        text = ""
        contains_faces = 0
        for image in images:
            contains_faces += self.scan_image_for_people(image)
            original, intelligible = self.scan_image_for_text(image)
            text += original
        return self.search_pii(text, contains_faces)

    def audio_handler(self):
        return self.plan_text_handler()

    def handle_timeout(self, signum, frame):
        raise TimeoutError("Operation timed out.")

    def main(self):
        
        # Create a multiprocessing.Manager
        manager = multiprocessing.Manager()
        # Create a multiprocessing.dict to store the result
        result_dict = manager.dict()
        # Create a multiprocessing.Process instance, passing the result_value as an argument
        process_instance = multiprocessing.Process(
            target=self.process, args=(result_dict,)
        )
        # Start the process
        process_instance.start()
        process_instance.join(timeout=settings.OCTOPII_TIMEOUT)

        # Wait for the process to finish or timeout

        # If the process is still alive after the timeout, terminate it
        if process_instance.is_alive():
            process_instance.kill()
            process_instance.join()

            # Raise a TimeoutError
            raise TimeoutError("Operation timed out.")

        # If the process completed within the timeout, retrieve the result
        return result_dict.copy()

    def process(self, result_dict):
        try:
            result = self.handlers[self.file_extension]()
            result_dict.update(result)
            return result
        except Exception as e:
            result_dict["error"] = repr(e)
            return e
