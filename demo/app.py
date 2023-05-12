import streamlit as st 
from load_database import *
from cogqa import *
import json
import requests
from streamlit_lottie import st_lottie  
from gg_search import *

@st.cache(allow_output_mutation=True)
def init_db():
    db = load_db()
    return db


@st.cache(allow_output_mutation=True)
def init_models(BERT_MODEL='bert-base-uncased', model_file='/Users/nguyen/Documents/AAAGNN/DemoCogQA/CogQA/models/bert-base-uncased.bin', max_new_nodes=5):
    setting = 'fullwiki' #if data_file.find('distractor') >= 0 else 'fullwiki'
    #with open(data_file, 'r') as fin:
     #   dataset = json.load(fin)
    tokenizer = BertTokenizer.from_pretrained(BERT_MODEL, do_lower_case=True)
    device = torch.device('cpu') #if not torch.cuda.is_available() else torch.device('cuda')
    print('Loading model from {}'.format(model_file))
    model_state_dict = torch.load(model_file, map_location=torch.device('cpu'))
    model1 = BertForMultiHopQuestionAnswering.from_pretrained(BERT_MODEL, state_dict=model_state_dict['params1'])
    model2 = CognitiveGNN(model1.config.hidden_size)
    model2.load_state_dict(model_state_dict['params2'])
    print('Start Training... on {} GPUs'.format(torch.cuda.device_count()))
    model1 = torch.nn.DataParallel(model1, device_ids = range(torch.cuda.device_count()))
    model1.to(device).eval()
    model2.to(device).eval()
    return tokenizer, model1, model2, device, setting



#dataset = copy.deepcopy(test[0])






#st.markdown("# Multi-hop Open-domain QA with [MDR](https://github.com/facebookresearch/multihop_dense_retrieval)")





# #st.markdown("*Trick: Due to the case sensitive tokenization we used during training, try to use capitalized entity names in your question, e.g., type United States instead of united states.*")

def predict(model1, model2, dataset, tokenizer, device, setting='fullwiki'):
    sp, answer, graphs = {}, {}, {}

    with torch.no_grad():
        for data in tqdm([dataset]):
            #st.write(data['question'])
            gold, ans, graph_ret, ans_nodes = cognitive_graph_propagate(tokenizer, data, model1, model2, device, setting = setting, max_new_nodes=5)
            
            context = dict(dataset['context'])

            # st.write('====================')
            #sp[data['_id']] = list(gold)
            #answer[data['_id']] = ans
            #graphs[data['_id']] = graph_ret + ['answer_nodes: ' + ', '.join(ans_nodes)]


    return gold, ans, graph_ret, ans_nodes, context
         
def main():
    st.set_page_config(
    page_title="Q&A",
    page_icon="❓",
    layout="wide",
    initial_sidebar_state="expanded"
    )
    db = init_db()
    tokenizer, model1, model2, device, setting = init_models()



    with open('/Users/nguyen/Documents/AAAGNN/DemoCogQA/CogQA/hotpot_test_fullwiki_v1_merge.json', 'r') as fin:
        test = json.load(fin)

    def load_lottieurl(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    lottie_mail = load_lottieurl("https://assets6.lottiefiles.com/packages/lf20_au4zdsr8.json")

    contact_icon, contact_link = st.columns((0.05, 0.16))
    with contact_icon:
        st_lottie(lottie_mail, height=80, key="mail")
    with contact_link:
        
        st.markdown("# Multi-hop QA with [Cognitive Graph](https://pythonandvba.com/contact)")
    st.markdown("*Trick: Due to the case sensitive tokenization we used during training, try to use capitalized entity names in your question, e.g., type United States instead of united states.*")
    #st.write("Streamlit version:", st.__version__)

  


    col1, col2 = st.columns([6, 4])
    with st.container():
        with col1:
            options = (test[0]['question'], test[1]['question'], test[2]['question'], test[3]['question'], test[4]['question'], test[5]['question'], test[6]['question'], test[7]['question'])
            index = st.selectbox("**CHOSE QUESTION**", range(len(options)), format_func=lambda x: options[x])

            st.write("❓ Question:", options[index])
            # st.write("index:", index)

            
            gold, ans, graph_ret, ans_nodes, context = predict(model1, model2, dataset=test[index], tokenizer=tokenizer, device=device, setting=setting)

            st.markdown(f'**💬 Answer**: {ans}')
            st.markdown(f'**Graph ret**:')

            st.write(graph_ret)

            st.markdown(f'**Ans node**:')

            st.write(ans_nodes)
        
        with col2:
            st.markdown(f'**Supporting passages**:')



            for e in list(gold):
                st.markdown(f'**{e}**:')
                try: 
                    for index in range(len(context[e[0]])):
                        
                        if (index == e[1]):
                            new_title = f'<p style="color:green; font-size: 17px;">{context[e[0]][e[1]]}</p>'
                            st.write(new_title, unsafe_allow_html=True)
                        else:
                            st.write(context[e[0]][index])
                except Exception as error:
                    st.error('Entity without context')
    
    st.markdown("# Find context")
    with st.form(key="text"):
        raw_review = st.text_area("Question")
        submit = st.form_submit_button(label="Submit")
    st.write("Submit: ", submit)
    if submit:
        search(raw_review)


  
            




# predict(model1, model2, tokenizer=tokenizer, dataset=test[index], device=device, setting=setting)
if __name__ == "__main__":
    main()
