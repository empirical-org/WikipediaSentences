import click

from quillopinion.opinioncheck import OpinionCheck

@click.command()
@click.argument('input_file')
@click.argument('output_file')
@click.option('--prompt', default=None, help='An optional prompt')
def main(input_file, output_file, prompt):
    check = OpinionCheck()

    with open(input_file) as i, open(output_file) as o:
        for line in i:
            sentence = line.strip()
            if prompt is not None:
                sentence = prompt + " " + sentence

            feedback = check.check_from_text(sentence, prompt)

            if len(feedback) > 0
                o.write(sentence + "\t" + prompt + "\t" + feedback[0].type + "\n")
            else:
                o.write(sentence + "\t" + prompt + "\tNO_OPINION\n")


if __name__ == "__main__":
    main()