
'''
    TODO: complete the following function to check whether the current post
          is relevant to the current topic
    topic - the topic that the user is interested in (e.g. BM25, PLSA, etc)
    text_vector - an array of strings representing current post
                  text_vector[0] = title of the post
                  text_vector[1] = main content of the post
                  text_vector[2:] = the students' answer, the instructors' answer, all other comments
    return value: True if relevant, False otherwise
'''


def isRelevant(topic, text_vector):
    if topic in text_vector[0] + text_vector[1] + text_vector[3]:
        return True
    return False

'''
    Calculates the similarity between a topic and a sentence([paragraph)
    topic - the topic that the user is interested in (e.g. BM25, PLSA, etc)
    sentence - a sentence that we want to know the similariy of
    return value: A number indicating the similarity.
'''
def calc_similarity(topic, sentence):
    # Need to be implemented better:
    # My idea: Suppose the topic is a k-gram word
    # Try to find the best matching from k-gram to (k-1, k-2) to 1-gram between the topic and the sentence
    # Best matching is defined as: whether a exact n-gram word appeared in sentence whenever n is >= 2.
    ## (Therefore this is either 0 or 1) and the highest similar word similarity for 1-gram word. (Real Value (0, 1))
    # Assign different weights to this matching: this part should be carefully designed
    # Below is a super naive version.
    if topic in sentence:
        return 1
    return 0


'''
    Calculates the similarity between a single! topic and a post
    topic - the topic that the user is interested in (e.g. BM25, PLSA, etc)
    text_vector - an array of strings representing current post
                  text_vector[0] = title of the post
                  text_vector[1] = main content of the post
                  text_vector[2:] = the students' answer, the instructors' answer, all other comments
    return value: A number indicating the similarity.
'''

def pure_score(topic, text_vector):
    # All number chosen arbitrary
    if topic == "":
        return 0.0
    _score = 0.0

    # Somewhere needs to be fixed, text vector should always contain at least 4 elements,
    # even if student/instructor do not answer.(that entry should be "")
    while text_vector.__len__() < 4:
        text_vector.append("")
    _score += 3 * calc_similarity(topic, text_vector[0]) + 2 * calc_similarity(topic, text_vector[1]) + \
              1.5 * calc_similarity(topic, text_vector[3]) + 1 * calc_similarity(topic, text_vector[2]) + \
              0.5*sum([calc_similarity(topic, _comment) for _comment in text_vector[4:]])
    return _score
