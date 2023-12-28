import openai 
import requests
import time


from bs4 import BeautifulSoup

from src.dict import dic_prensa_españa,dic_prensa_inter

# URL del periódico web que quieres hacer scraping
def scrap_news(inter = True):

    if inter: 
        dicc_newsp = dic_prensa_inter
    else:
        dic_prensa_españa

    news_dict = {}

    for newsp, newsp_dic in dicc_newsp.items():

        news_list = []
        url = newsp_dic['url']
        html_class_key = newsp_dic['class']
        cookies = newsp_dic['cookies']
        headers = newsp_dic['headers']
        sep = newsp_dic['sep']

        # Enviar una solicitud para obtener el contenido de la página
        response = requests.get(url, cookies=cookies, headers=headers)

        # Verificar si la solicitud fue exitosa (código de estado 200)
        if response.status_code == 200:
            # Parsear el contenido HTML de la página usando BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Encontrar elementos en la página (por ejemplo, títulos de noticias)
            titulos = soup.find_all(sep, class_= html_class_key)

            # Imprimir los títulos de las noticias
            for titulo in titulos[:30]:
                news_list.append(titulo.text)
        
            news_dict[newsp] = news_list
        #     print (f'{newsp} : {len(news_list)} titulares')
        # else:
        #     print(f'Error: {newsp}/ status code {response.status_code}')
        
    # Claves que deseas combinar
    key_combine1 = 'wsj'
    key_combine2 = 'wsj2'

    # Unir las listas correspondientes
    if key_combine1 in news_dict and key_combine2 in news_dict:
        lista_combinada = news_dict[key_combine1] + news_dict[key_combine2]
        news_dict[key_combine1] = lista_combinada
        del news_dict[key_combine2]


    return news_dict


def get_subjects(news_dict):

    combined_list=[]
    sub_list=[]
    for _ , list_news in news_dict.items():
        combined_list.extend(list_news)

    # openai.api_key = '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'
    client = openai.OpenAI()

    for i in range(int(len(combined_list)/100)+1):
        num=100
        num_temas=4
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
        messages=[
            # {"role": "system", "content": f" la estructura de tu respuesta tiene que ser  unicamente:    tema 1-tema 2-..-tema {num_temas*num} . los temas tiene que ser especificos por ejemplo nombres de personas o empresas y no pueden ser diferentes para el mismo nombre. evita poner temas poco especificos como politica, bolsa, gobierno"},
            # {"role": "user", "content": f"Para cada articulo de esta lista de titulares del periodico {combined_list[num*i:min(len(combined_list),num*(i+1))]} dime {num_temas} temas por articulo  "}
            {"role": "system","content": f"The structure of your response should be only: topic 1-topic 2-...-topic {num_temas*num}. Topics must be specific, such as names of people or companies, and should not differ for the same name. Avoid using unspecific topics like politics, stock market, government."},
            {"role": "user","content": f"For each article from this list of newspaper headlines {combined_list[num*i:min(len(combined_list),num*(i+1))]}, tell me {num_temas} topics per article."}
        ]
        )
        sub_list.extend(completion.choices[0].message.content.replace('\n', '-').replace(" '", '').replace("' ", '').replace("'", '').split('-'))
        if i !=int(len(combined_list)/100):
            time.sleep(21)
    sub_list=[x[1:] if x[:1]==' 'else x for x in sub_list]

    return sub_list