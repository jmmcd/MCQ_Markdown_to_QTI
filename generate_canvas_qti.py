import re
import zipfile
import uuid
from lxml import etree as ET
from pathlib import Path
import argparse

def parse_mcqs(text):
    """Parse numbered MCQ text with + marking correct answers"""
    questions = []
    
    # Split by question numbers
    pattern = r'^\d+\.\s+'
    blocks = re.split(pattern, text, flags=re.MULTILINE)
    blocks = [b.strip() for b in blocks if b.strip()]
    
    for block in blocks:
        lines = block.split('\n')
        
        question_lines = []
        choices = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('*') or line.startswith('+'):
                while i < len(lines):
                    line = lines[i].strip()
                    if line.startswith('*') or line.startswith('+'):
                        is_correct = line.startswith('+')
                        choice_text = line[1:].strip()
                        if choice_text:
                            choices.append({
                                'text': choice_text,
                                'correct': is_correct
                            })
                    i += 1
                break
            elif line:
                question_lines.append(line)
            
            i += 1
        
        if question_lines and choices:
            questions.append({
                'question': '\n'.join(question_lines),
                'choices': choices
            })
    
    return questions

def format_text_with_code(text):
    """Convert markdown code to HTML"""
    # Code blocks
    text = re.sub(r'```\n?(.*?)\n?```', r'<pre>\1</pre>', text, flags=re.DOTALL)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Convert newlines to paragraphs
    paragraphs = text.split('\n')
    if len(paragraphs) > 1:
        text = ''.join(f'<p>{p}</p>' if p.strip() else '' for p in paragraphs)
    elif text and not text.startswith('<'):
        text = f'<p>{text}</p>'
    
    return text

def create_canvas_manifest(assessment_id):
    """Create Canvas-compatible imsmanifest.xml"""
    manifest = ET.Element('manifest',
                         identifier=str(uuid.uuid4().hex),
                         nsmap={
                             None: 'http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1',
                             'lom': 'http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource',
                             'imsmd': 'http://www.imsglobal.org/xsd/imsmd_v1p2',
                             'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
                         })
    manifest.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
                 'http://www.imsglobal.org/xsd/imsccv1p1/imscp_v1p1 http://www.imsglobal.org/xsd/imscp_v1p1.xsd '
                 'http://ltsc.ieee.org/xsd/imsccv1p1/LOM/resource http://www.imsglobal.org/profile/cc/ccv1p1/LOM/ccv1p1_lomresource_v1p0.xsd '
                 'http://www.imsglobal.org/xsd/imsmd_v1p2 http://www.imsglobal.org/xsd/imsmd_v1p2p2.xsd')
    
    metadata = ET.SubElement(manifest, 'metadata')
    schema = ET.SubElement(metadata, 'schema')
    schema.text = 'IMS Content'
    schemaversion = ET.SubElement(metadata, 'schemaversion')
    schemaversion.text = '1.1.3'
    
    lom = ET.SubElement(metadata, '{http://www.imsglobal.org/xsd/imsmd_v1p2}lom')
    general = ET.SubElement(lom, '{http://www.imsglobal.org/xsd/imsmd_v1p2}general')
    title = ET.SubElement(general, '{http://www.imsglobal.org/xsd/imsmd_v1p2}title')
    string_elem = ET.SubElement(title, '{http://www.imsglobal.org/xsd/imsmd_v1p2}string')
    string_elem.text = 'QTI Quiz Export'
    
    organizations = ET.SubElement(manifest, 'organizations')
    resources = ET.SubElement(manifest, 'resources')
    
    meta_id = str(uuid.uuid4().hex)
    
    # Main assessment resource
    resource = ET.SubElement(resources, 'resource',
                            identifier=assessment_id,
                            type='imsqti_xmlv1p2')
    file_elem = ET.SubElement(resource, 'file',
                             href=f'{assessment_id}/{assessment_id}.xml')
    dependency = ET.SubElement(resource, 'dependency', identifierref=meta_id)
    
    # Meta resource
    meta_resource = ET.SubElement(resources, 'resource',
                                 identifier=meta_id,
                                 type='associatedcontent/imscc_xmlv1p1/learning-application-resource',
                                 href=f'{assessment_id}/assessment_meta.xml')
    file_elem = ET.SubElement(meta_resource, 'file',
                             href=f'{assessment_id}/assessment_meta.xml')
    
    return manifest

def create_assessment_meta(assessment_id, title='Python MCQs'):
    """Create Canvas assessment_meta.xml"""
    quiz = ET.Element('quiz',
                     identifier=assessment_id,
                     nsmap={
                         None: 'http://canvas.instructure.com/xsd/cccv1p0',
                         'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
                     })
    quiz.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
            'http://canvas.instructure.com/xsd/cccv1p0 https://canvas.instructure.com/xsd/cccv1p0.xsd')
    
    title_elem = ET.SubElement(quiz, 'title')
    title_elem.text = title
    
    ET.SubElement(quiz, 'description')
    ET.SubElement(quiz, 'shuffle_questions').text = 'false'
    ET.SubElement(quiz, 'shuffle_answers').text = 'false'
    ET.SubElement(quiz, 'quiz_type').text = 'assignment'
    ET.SubElement(quiz, 'points_possible').text = '1.0'
    ET.SubElement(quiz, 'allowed_attempts').text = '1'
    ET.SubElement(quiz, 'scoring_policy').text = 'keep_highest'
    
    return quiz

def create_qti_assessment(questions, assessment_id, title='Python MCQs'):
    """Create Canvas QTI 1.2 assessment"""
    
    questestinterop = ET.Element('questestinterop',
                                nsmap={
                                    None: 'http://www.imsglobal.org/xsd/ims_qtiasiv1p2',
                                    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
                                })
    questestinterop.set('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
                       'http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd')
    
    assessment = ET.SubElement(questestinterop, 'assessment',
                              ident=assessment_id,
                              title=title)
    
    section = ET.SubElement(assessment, 'section', ident='root_section')
    
    for idx, q_data in enumerate(questions, 1):
        item_id = str(uuid.uuid4().hex)
        
        item = ET.SubElement(section, 'item',
                            ident=item_id,
                            title=f'Question {idx}')
        
        # Item metadata
        itemmetadata = ET.SubElement(item, 'itemmetadata')
        qtimetadata = ET.SubElement(itemmetadata, 'qtimetadata')
        
        # Question type - detect from question text
        field = ET.SubElement(qtimetadata, 'qtimetadatafield')
        ET.SubElement(field, 'fieldlabel').text = 'question_type'
        
        # Check if multiple answers based on keywords in question
        q_text_lower = q_data['question'].lower()
        is_multiple = any(phrase in q_text_lower for phrase in [
            'select all',
            'choose all',
            'select multiple',
            'zero, one, or more',
            'zero, one or more', # LOL Claude enjoys an Oxford comma
            'one or more',
            'check all',
            'mark all'
        ])
        
        q_type = 'multiple_answers_question' if is_multiple else 'multiple_choice_question'
        ET.SubElement(field, 'fieldentry').text = q_type
        
        # Points
        field = ET.SubElement(qtimetadata, 'qtimetadatafield')
        ET.SubElement(field, 'fieldlabel').text = 'points_possible'
        ET.SubElement(field, 'fieldentry').text = '1.0'
        
        # Presentation
        presentation = ET.SubElement(item, 'presentation')
        
        # Question text
        material = ET.SubElement(presentation, 'material')
        mattext = ET.SubElement(material, 'mattext', texttype='text/html')
        formatted_q = format_text_with_code(q_data['question'])
        mattext.text = formatted_q
        
        # Response
        response_lid = ET.SubElement(presentation, 'response_lid',
                                    ident='response1',
                                    rcardinality='Multiple' if is_multiple else 'Single')
        render_choice = ET.SubElement(response_lid, 'render_choice')
        
        choice_ids = []
        for choice in q_data['choices']:
            choice_id = str(uuid.uuid4())
            choice_ids.append((choice_id, choice['correct']))
            
            response_label = ET.SubElement(render_choice, 'response_label',
                                          ident=choice_id)
            material = ET.SubElement(response_label, 'material')
            mattext = ET.SubElement(material, 'mattext', texttype='text/html')
            formatted_choice = format_text_with_code(choice['text'])
            mattext.text = formatted_choice
        
        # Response processing
        resprocessing = ET.SubElement(item, 'resprocessing')
        outcomes = ET.SubElement(resprocessing, 'outcomes')
        ET.SubElement(outcomes, 'decvar',
                     maxvalue='100',
                     minvalue='0',
                     varname='SCORE',
                     vartype='Decimal')
        
        # Correct answers
        for choice_id, is_correct in choice_ids:
            if is_correct:
                respcondition = ET.SubElement(resprocessing, 'respcondition',
                                             attrib={'continue': 'No'})
                conditionvar = ET.SubElement(respcondition, 'conditionvar')
                varequal = ET.SubElement(conditionvar, 'varequal',
                                        respident='response1')
                varequal.text = choice_id
                ET.SubElement(respcondition, 'setvar',
                             action='Set',
                             varname='SCORE').text = '100'
    
    return questestinterop

def main():
    parser = argparse.ArgumentParser(
        description='Convert MCQ markdown to Canvas QTI format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python generate_canvas_qti.py --input MCQs.md --output MCQs_QTI.zip

MCQ Format:
  - Questions numbered: 1. Question text?
  - Answers marked with * (incorrect) or + (correct)
  - Use backticks for code: `code` or ```code blocks```
  - Multiple-answer questions detected by keywords:
    "select all", "zero, one, or more", etc.
        """
    )
    parser.add_argument('--input', '-i', required=True,
                       help='Input markdown file with MCQs')
    parser.add_argument('--output', '-o', required=True,
                       help='Output QTI zip file')
    parser.add_argument('--title', '-t', default='Python MCQs',
                       help='Quiz title (default: Python MCQs)')
    
    args = parser.parse_args()
    
    # Read MCQs file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found")
        return 1
    
    with open(input_path, 'r') as f:
        content = f.read()
    
    # Parse questions
    questions = parse_mcqs(content)
    print(f"Parsed {len(questions)} questions")
    
    if not questions:
        print("Error: No questions found in input file")
        return 1
    
    assessment_id = 'g' + uuid.uuid4().hex
    
    # Create temporary directory for QTI files
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        assessment_dir = output_dir / assessment_id
        assessment_dir.mkdir(exist_ok=True)
        
        # Create manifest
        manifest = create_canvas_manifest(assessment_id)
        manifest_tree = ET.ElementTree(manifest)
        manifest_tree.write(output_dir / 'imsmanifest.xml',
                           pretty_print=True,
                           xml_declaration=True,
                           encoding='UTF-8')
        
        # Create assessment meta
        meta = create_assessment_meta(assessment_id, args.title)
        meta_tree = ET.ElementTree(meta)
        meta_tree.write(assessment_dir / 'assessment_meta.xml',
                       pretty_print=True,
                       xml_declaration=True,
                       encoding='UTF-8')
        
        # Create assessment
        assessment = create_qti_assessment(questions, assessment_id, args.title)
        assessment_tree = ET.ElementTree(assessment)
        assessment_tree.write(assessment_dir / f'{assessment_id}.xml',
                             pretty_print=True,
                             xml_declaration=True,
                             encoding='UTF-8')
        
        # Create zip
        output_path = Path(args.output)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(output_dir / 'imsmanifest.xml', 'imsmanifest.xml')
            zipf.write(assessment_dir / 'assessment_meta.xml',
                      f'{assessment_id}/assessment_meta.xml')
            zipf.write(assessment_dir / f'{assessment_id}.xml',
                      f'{assessment_id}/{assessment_id}.xml')
        
        print(f"Created: {output_path}")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
