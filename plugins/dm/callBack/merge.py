'''

█ █▄ █    █▄█ ▄▀▄ █▄ ▄█ ██▀    █▀▄ █▀▄ █▀ 
█ █ ▀█    █ █ █▀█ █ ▀ █ █▄▄    █▀  █▄▀ █▀ 
                        Dev : IlhamGUD

'''

import os
import time
import shutil
from time import sleep
from pdf import PROCESS
from pyromod import listen
from pyrogram import filters
from Configs.dm import Config
from PyPDF2 import PdfFileMerger
from plugins.checkPdf import checkPdf
from plugins.progress import progress
from pyrogram import Client as InHamePDF
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup




#--------------->
#--------> LOCAL VARIABLES
#------------------->

MERGE = {}; MERGEsize = {}

if Config.MAX_FILE_SIZE:
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE"))
    MAX_FILE_SIZE_IN_kiB = MAX_FILE_SIZE * (10**6)
else:
    MAX_FILE_SIZE = False

PDF_THUMBNAIL = Config.PDF_THUMBNAIL

#--------------->
#--------> MERGE PDFS
#------------------->


merge = filters.create(lambda _, __, query: query.data == "merge")


@InHamePDF.on_callback_query(merge)
async def _merge(bot, callbackQuery):
    try:
        # CHECK IF BOT DOING ANY WORK
        if callbackQuery.message.chat.id in PROCESS:
            await callbackQuery.answer(
                "⏳ - Sedang dalam proses"
            )
            return
        # ADD TO PROCESS
        PROCESS.append(callbackQuery.message.chat.id)
        fileId=callbackQuery.message.reply_to_message.document.file_id
        fileSize=callbackQuery.message.reply_to_message.document.file_size
        fileNm=callbackQuery.message.reply_to_message.document.file_name
        fileNm, fileExt=os.path.splitext(fileNm)        # seperates name & extension
        # ADDING FILE ID & SIZE TO MERGE, MERGEsize LIST (FOR FUTURE USE)
        MERGE[callbackQuery.message.chat.id]=[fileId]
        MERGEsize[callbackQuery.message.chat.id]=[fileSize]
        # REQUEST FOR OTHER PDFS FOR MERGING
        inhame=True; size=0
        while(inhame):
            if len(MERGE[callbackQuery.message.chat.id]) >= 5:
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "__❗ - Karena Overload, Anda hanya dapat menggabungkan 5 pdf sekaligus__"
                )
                inhame = False
                break
            askPDF = await bot.ask(
                text = "__MERGE pdfs » Jumlah pdf dalam antrian: {}__\n\n/keluar __untuk membatalkan__\n/merge __untuk merge__".format(
                    len(MERGE[callbackQuery.message.chat.id])
                ),
                chat_id = callbackQuery.message.chat.id,
                reply_to_message_id = callbackQuery.message.message_id,
                filters = None
            )
            if askPDF.text == "/keluar":
                await bot.send_message(
                    callbackQuery.message.chat.id,
                    "`☑️ - Proses dibatalkan`"
                )
                PROCESS.remove(callbackQuery.message.chat.id)
                del MERGE[callbackQuery.message.chat.id]
                del MERGEsize[callbackQuery.message.chat.id]
                break
            if askPDF.text == "/merge":
                inhame = False
                break
            # IS SEND MESSAGE A DOCUMENT
            if askPDF.document:
                file_id=askPDF.document.file_id
                file_size=askPDF.document.file_size
                # CHECKING FILE EXTENSION .pdf OR NOT
                if fileExt == ".pdf":
                    # CHECKING TOTAL SIZE OF MERGED PDF
                    for _ in MERGEsize[callbackQuery.message.chat.id]:
                        size = int(_) + size
                    # CHECKS MAXIMUM FILE SIZE (IF ADDED) ELSE 1.8 GB LIMIT
                    if (MAX_FILE_SIZE and MAX_FILE_SIZE_IN_kiB <= int(size)) or int(size) >= 1800000000:
                        await bot.send_message(
                            callbackQuery.message.chat.id,
                            f"`Karena overload bot hanya mendukung %sMb pdf..`"%(MAX_FILE_SIZE if MAX_FILE_SIZE else "1.8Gb")
                        )
                        inhame=False
                        break
                    # ADDING NEWLY ADDED PDF FILE ID & SIZE TO LIST
                    MERGE[callbackQuery.message.chat.id].append(file_id)
                    MERGEsize[callbackQuery.message.chat.id].append(file_size)
        # inhame=True ONLY IF PROCESS CANCELLED
        if inhame == True:
            PROCESS.remove(callbackQuery.message.chat.id)
        # GET /merge, REACHES MAX FILE SIZE OR MAX NO OF PDF
        if inhame == False:
            # DISPLAY TOTAL PDFS FOR MERGING
            downloadMessage = await callbackQuery.message.reply_text(
                f"`Total PDF : {len(MERGE[callbackQuery.message.chat.id])}`",
                quote=True
            )
            sleep(.5)
            i = 0
            # ITERATIONS THROUGH FILE ID'S AND DOWNLOAD
            for iD in MERGE[callbackQuery.message.chat.id]:
                await downloadMessage.edit(
                    f"__Memulai mendownload Pdf :{i+1}__"
                )
                # START DOWNLOAD
                c_time=time.time()
                downloadLoc=await bot.download_media(
                    message=iD,
                    file_name=f"merge{callbackQuery.message.chat.id}/{i}.pdf",
                    progress=progress,
                    progress_args=(
                        MERGEsize[callbackQuery.message.chat.id][i],
                        downloadMessage,
                        c_time
                    )
                )
                # CHECKS IF DOWNLOAD COMPLETE/PROCESS CANCELLED
                if downloadLoc is None:
                    PROCESS.remove(callbackQuery.message.chat.id)
                    await callbackQuery.message.reply_text(
                        "`Merge Process Cancelled.. 😏`", quote=True
                    )
                    shutil.rmtree(f"merge{callbackQuery.message.chat.id}")
                    return
                # CHECKS PDF CODEC, ENCRYPTION..
                checked = await checkPdf(
                    f"merge{callbackQuery.message.chat.id}/{i}.pdf",
                    callbackQuery
                )
                # REMOVE FILE FROM DIRECTORY IF FILE NOT ENCRYPTED OR CODECERROR
                if not(checked == "pass"):
                    os.remove(f"merge{callbackQuery.message.chat.id}/{i}.pdf")
                i += 1
            directory = f'merge{callbackQuery.message.chat.id}'
            pdfList = [os.path.join(directory, file) for file in os.listdir(directory)]
            # SORT DIRECTORY PATH BY ITS MODIFIED TIME
            pdfList.sort(key=os.path.getctime)
            numbPdf = len(pdfList)
            # MERGING STARTED
            await downloadMessage.edit(
                "__Merging Started.. __ 🪄"
            )
            output_pdf=f"merge{callbackQuery.message.chat.id}/merge.pdf"
            #PyPDF 2
            merger = PdfFileMerger()
            for i in pdfList:
                merger.append(i)
            merger.write(output_pdf)
            # STARTED UPLOADING
            await downloadMessage.edit(
                "`📤 - Mengirim file`"
            )
            await bot.send_chat_action(
                callbackQuery.message.chat.id, "upload_document"
            )
            # SEND DOCUMENT
            await bot.send_document(
                file_name=f"{fileNm}.pdf",
                chat_id=callbackQuery.message.chat.id,
                document=open(output_pdf, "rb"),
                thumb=PDF_THUMBNAIL, caption="__merged pdf__"
            )
            await downloadMessage.delete()
            shutil.rmtree(f"merge{callbackQuery.message.chat.id}")
            PROCESS.remove(callbackQuery.message.chat.id)
    except Exception as e:
        try:
            print("plugins/dms/cllba/merge: ", e)
            shutil.rmtree(f"merge{callbackQuery.message.chat.id}")
            PROCESS.remove(callbackQuery.message.chat.id)
        except Exception:
            pass


# Copyright InHame Dev
