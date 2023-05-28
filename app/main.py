import flask
import os
from __init__ import create_app
from flask import send_from_directory, request
from controller import *

app = create_app()

@app.route("/")
def home():
    return "Hello World"


@app.route("/webhook", methods=["POST"])
def handleWebhook():
    req = request.get_json(force=True)
    # print(req)

    query_text = req["queryResult"]["queryText"]
    intent = req["queryResult"]["intent"]["displayName"]

    if "title" in req["queryResult"]["parameters"]:
        user_param = req["queryResult"]["parameters"]["title"]
        # print(user_param)

        books_from_partial = get_id_from_partial_name(user_param)
        # print(books_from_partial)

        list_recommendation = []
        if len(books_from_partial) == 0:
            res = {
                "fulfillmentMessages": [
                    {
                        "payload": {
                            "telegram": {
                                "reply_markup": {
                                    "inline_keyboard": [
                                        [
                                            {
                                                "callback_data": "minta rekomendasi buku",
                                                "text": "Ulangi Permintaan",
                                            }
                                        ],
                                        [
                                            {
                                                "callback_data": "tidak ada",
                                                "text": "Lihat judul lainnya",
                                            }
                                        ],
                                    ]
                                },
                                "text": "Maaf, Sibook tidak dapat menemukan buku yang kamu inginkan.\n\nSilahkan untuk ulangi permintaan atau lihat pilihan judul buku lainnya.",
                            }
                        },
                        "platform": "TELEGRAM",
                    }
                ],
                "outputContexts": [
                    {
                        "name": "projects/bookrec-agent-dbci/agent/sessions/f25e9266-09bb-156c-947c-6fd88e269d95/contexts/askrecommendation-followup",
                        "lifespanCount": 2,
                    }
                ],
            }

        elif len(books_from_partial) == 1:
            list_recommendation = get_top_similarities(books_from_partial[0], model)
            recommendation_list = list_recommendation.to_numpy()
            # print(recommendation_list)

            image = find_book_image(recommendation_list)
            # print(image)

            res = {
                "fulfillmentMessages": [
                    {
                        "payload": {
                            "telegram": {
                                "text": f'Judul preferensi: "{books_from_partial[0]}".\n\nTunggu sebentar ya, akan Sibook carikan rekomendasi buku untukmu.',
                                "parse_mode": "Markdown",
                            },
                            "platform": "TELEGRAM",
                        }
                    },
                    {
                        "payload": {
                            "telegram": {
                                "text": "Berikut beberapa buku rekomendasi yang Sibook bisa berikan.",
                                "parse_mode": "Markdown",
                            },
                            "platform": "TELEGRAM",
                        }
                    },
                    {
                        "payload": {
                            "telegram": {
                                "text": f'<strong>1. {recommendation_list[0]}</strong><a href="{image[0]}">.</a>',
                                "parse_mode": "HTML",
                            },
                            "platform": "TELEGRAM",
                        }
                    },
                    {
                        "payload": {
                            "telegram": {
                                "text": f'<strong>2. {recommendation_list[1]}</strong><a href="{image[1]}">.</a>',
                                "parse_mode": "HTML",
                            },
                            "platform": "TELEGRAM",
                        }
                    },
                    {
                        "payload": {
                            "telegram": {
                                "text": f'<strong>3. {recommendation_list[2]}</strong><a href="{image[2]}">.</a>',
                                "parse_mode": "HTML",
                            },
                            "platform": "TELEGRAM",
                        }
                    },
                    {
                        "payload": {
                            "telegram": {
                                "text": f'<strong>4. {recommendation_list[3]}</strong><a href="{image[3]}">.</a>',
                                "parse_mode": "HTML",
                            },
                            "platform": "TELEGRAM",
                        }
                    },
                    {
                        "payload": {
                            "telegram": {
                                "text": f'<strong>5. {recommendation_list[4]}</strong><a href="{image[4]}">.</a>',
                                "parse_mode": "HTML",
                            },
                            "platform": "TELEGRAM",
                        }
                    },
                    {
                        "payload": {
                            "telegram": {
                                "text": "Tips: Jika preview buku tidak ada, silahkan pindah ke halaman chat lain lalu kembali halaman chat ini untuk merefresh.",
                                "parse_mode": "Markdown",
                            },
                            "platform": "TELEGRAM",
                        }
                    },
                    {
                        "payload": {
                            "telegram": {
                                "text": "Gimana nih kak, apakah kamu suka dengan hasil rekomendasinya?",
                                "parse_mode": "Markdown",
                            },
                            "platform": "TELEGRAM",
                        }
                    },
                ]
            }

        else:
            response_text = (
                "Sibook menemukan beberapa judul yang mirip dengan pilihan kamu.\n\n"
            )

            if len(books_from_partial) > 10:
                for i in range(10):
                    response_text += f"{i+1}. {books_from_partial[i]}\n"
            else:
                for i in range(len(books_from_partial)):
                    response_text += f"{i+1}. {books_from_partial[i]}\n"

            response_text += "\nSilahkan pilih judul buku yang tersedia."

            res = {
                "fulfillmentMessages": [
                    {
                        "payload": {
                            "telegram": {
                                "reply_markup": {
                                    "inline_keyboard": [
                                        [
                                            {
                                                "callback_data": "ada",
                                                "text": "Pilih judul",
                                            }
                                        ]
                                    ]
                                },
                                "text": f"{response_text}",
                            }
                        },
                        "platform": "TELEGRAM",
                    }
                ],
                "outputContexts": [
                    {
                        "name": "projects/bookrec-agent-dbci/agent/sessions/f25e9266-09bb-156c-947c-6fd88e269d95/contexts/askrecommendation-followup",
                        "lifespanCount": 2,
                    }
                ],
            }

    else:
        item_list = list(high_rate_book["Book title"].sample(n=5))
        # print(item_list)

        response_text = "Berikut beberapa judul buku yang bisa kamu jadikan preferensi, silahkan pilih jika judulnya menarik untuk kamu.\n\n"

        for i in range(len(item_list)):
            response_text += f"{i+1}. {item_list[i]}\n"

        res = {
            "fulfillmentMessages": [
                {
                    "payload": {
                        "telegram": {
                            "reply_markup": {
                                "inline_keyboard": [
                                    [{"text": "Pilih judul", "callback_data": "Ada"}],
                                    [
                                        {
                                            "text": "Lihat lainnya",
                                            "callback_data": "Tidak ada",
                                        }
                                    ],
                                ]
                            },
                            "text": f"{response_text}",
                            "parse_mode": "Markdown",
                        },
                        "platform": "TELEGRAM",
                    }
                },
            ],
        }

    return res


if __name__ == "__main__":
    app.run()
