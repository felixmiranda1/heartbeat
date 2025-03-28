from django import template

register = template.Library()

@register.filter
def get_item(d, key):
    if isinstance(d, dict):
        return d.get(key)
    return None

# Dicionário de tradução para labels
label_translations = {
    "Name": "Nome",
    "Birth date": "Data de Nasc.",
    "Gender": "Sexo",
    "Contact": "Contato",
    "Height": "Altura",
    "Weight": "Peso",
    "Date": "Data da Consulta",
    "Examiner": "Examinador",
    "Clinic": "Clínica",
    "Professional": "Profissional",
    "Procedure": "Procedimento",
    "Health insurance": "Operadora",
    "Insurance plan": "Plano de Saúde",
    "Requester": "Solicitante",
    "Observations": "Observações",
}

@register.filter(name='dict_translate')
def dict_translate(value):
    return label_translations.get(value, value)