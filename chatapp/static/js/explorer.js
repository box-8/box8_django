
var analyse_courante = {"username":"","analyse":"","entries":[],"prompt":"", "history":[]} 
var fichier_courant ={"filename":""}

const turndownService = new TurndownService({ headingStyle: 'atx' });;


// Global functions
function getCookie(name) {
  const cookieValue = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
  return cookieValue ? cookieValue.pop() : '';
}

$(document).ready(function () {
    toastPosition = "top-left"
    
    // vide les listes analyse ou fiches
    function explorerEmpty(target){
      $("#"+target).html("")
    }

    // remplit les listes analyses et fiches 
    function explorerPopulate(target,json){
      explorerEmpty(target)
      console.log("explorerPopulate",json)
      
      $.each(json.entries, function (index, entry) {
        let listItem = $("<a href='javascript:void(0);' class='list-group-item'>" + entry.caption + "</a>")
        listItem.attr("id",entry.type+"-"+entry.id)

        if(entry.type=="analyse"){
          listItem.addClass("list-group-item-analyse")
          listItem.click(function(){
            $(".list-group-item-analyse").removeClass("active")
            $(this).addClass("active")
            dossier_analyse = entry.caption
            // $("#fiches-tab").html("Dossier : " + entry.caption)
            $("#fiches-panel-title").html(entry.caption)
            chatapp_ajax_set_analyse(dossier_analyse)
            ongletFichierEmpty()
          });
          listItem.on( "dblclick", function() {
            $("#fiches-tab").click()
          });
          

        }else if(entry.type=="new_analyse"){

        }else{ // type = document
          if (! entry.memorized) {listItem.addClass("list-group-item-warning");}
          listItem.addClass("list-group-item-document")
          // listItem.attr("title","double click pour charger les informations de la vectorisation")
          listItem.click(function(){
            clearMarkers()
            ongletFichierEmpty()
            fichier_courant.filename = entry.caption
            fichier_courant.id = entry.type+"-"+entry.id
            var capt = entry.caption
            if(capt.length > 35){capt = entry.caption.substring(0, 35)+"..."}
            // $("#fichier-tab").html(capt)
            $("#fichier-panel-title").html(entry.caption)
            chatapp_set_fiches(entry.parent_analyse) 
            $("#viewer-iframe").click(function(){
              url='/sharepoint/'+analyse_courante.username+'/'+ entry.parent_analyse+'/'+entry.caption
              window.open(url, 'viewerIframe');
            })

            if (! entry.memorized) {
              $(".list-group-item-document").removeClass("active")
              //chatapp_memorize_doc(listItem, entry)
              $.toast({heading: "Info",text: "Le document n'est pas vectorisé",position: toastPosition ,icon: "info", stack: true})
              $("#fichier-tab").click()
            }else{
              // $(this).toggleClass("active")
              $(".list-group-item-document").removeClass("active")
              $(this).addClass("active")
              chatapp_get_fichedetails(entry)
              
            }
          });
          listItem.on( "dblclick", function() {
            $("#fiches-tab").click()
          });
        }
        $("#"+target).append(listItem);
      });
    }

    
    
    
    // stocke les fichiers sélectionnées dans analyse_courante.entries pour les poster au serveur 
    function chatapp_set_fiches(analyse){
      analyse_courante.analyse = analyse
      // var additionalData = {"analyse":analyse, "entries":[]}
      var newEntries = []
      $("#explorer_fiches .active").each(function(){
        newEntries.push($(this).html())
      })
      analyse_courante.entries = newEntries;
      return false
    }


    // fonction commune $("#viewer-vectoriser").click et $("#viewer-delete").click
    function get_fichier_courant(){
      if (fichier_courant.filename==""){
        $.toast({heading: "Erreur",text: "Choisir un fichier",position: toastPosition,icon: "warning", stack: true}) 
        return false
      }
      var listItem = $(".list-group-item-document:contains('"+ fichier_courant.filename +"')");
      if (listItem.length !=1){
        console.log("Erreur")
        return false
      }
      var entry = {}
      entry.parent_analyse = analyse_courante.analyse
      entry.caption = fichier_courant.filename
      entry.memorized= !listItem.hasClass("list-group-item-warning")
      entry.type = "document"
      
      var return_object={}
      return_object.entry = entry
      return_object.listItem = listItem
      return return_object
    }

    $("#viewer-vectoriser").click(function(){
      curfile = get_fichier_courant()
      if (curfile===false){
        $.toast({heading: "Erreur",text: "Choisir un fichier",position: toastPosition,icon: "danger", stack: true})
      }else{
        console.log("OK memorize", curfile)
        chatapp_memorize_doc(curfile.listItem, curfile.entry)
      }
      
    })
    
    // lance la vectorisation d'un document en async
    function chatapp_memorize_doc(listItem, entry){
      let pages = prompt("Entrez le nombre de pages que vous souhaiter résumer :", "6");
      analyse_courante.prompt=pages
      analyse_courante.analyse = entry.parent_analyse
      analyse_courante.entries = [entry.caption]
      console.log("chatapp_memorize_doc",analyse_courante)
      chatapp_memorize_doc_ajax(listItem, entry)
      
    }

    function chatapp_memorize_doc_ajax(listItem, entry){
      
      $.ajax({
        url: chatapp_summarize,
        type: 'POST',
        data: JSON.stringify(analyse_courante), 
        contentType: 'application/json', 
        beforeSend: function(xhr, settings){
          xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        success: function (response) {
          $.toast({heading: "résumé réalisé",text: "le résumé est disponible dans insights",position: toastPosition,icon: response.state, stack: true,hideAfter: 5000})
          if(listItem !== undefined){listItem.removeClass("list-group-item-warning")}
          if(entry !== undefined){entry.memorized = true}
          
          html = marked.parse(response.content)
          $("#filedetails").html(html)
          console.log(response);
          chatapp_ajax_set_analyse(analyse_courante.analyse)
        },
        error: function () {
        }
      });
    }

    $("#viewer-delete").click(function(){
      curfile = get_fichier_courant()
      if (curfile===false){
        $.toast({heading: "Erreur",text: "Choisir le fichier à effacer",position: toastPosition,icon: "danger", stack: true})
      }else{
        console.log("OK delete", curfile)
        chatapp_delete_doc(curfile.listItem, curfile.entry)
      }

    });
    
    function chatapp_delete_doc(listItem, entry){
      analyse_courante.analyse = entry.parent_analyse
      analyse_courante.entries = [entry.caption]
      var confirmation = confirm("Êtes-vous sûr de vouloir supprimer le document ? \n"+ entry.caption);
      if (confirmation) {
        $.ajax({
          url: chatapp_delete_file,
          type: 'POST',
          data: JSON.stringify(analyse_courante), 
          contentType: 'application/json', 
          beforeSend: function(xhr, settings){
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
          },
          success: function (response) {
            console.log(response);
            explorerPopulate("explorer_fiches",response)
            ongletFichierEmpty()
          },
          error: function () {
            ongletFichierEmpty()
          }
        });
      }
    }

    function ongletFichierEmpty(){
      $("#fichier-tab").html("Fichier")
      $("#fichier-panel-title").html("")
      $("#filedetails").html("Pas de contenu, sélectionner un fichier dans l'onglet Analyse")
    }
    
    // obtient le détail du dernier fichier séléctionné
    function chatapp_get_fichedetails(entry){
      analyse_courante.analyse = entry.parent_analyse
      analyse_courante.entries = [entry.caption]
      var url = afficher_resume_vectorisation.replace('0', entry.parent_analyse).replace('0', entry.caption);
      $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(analyse_courante), 
        contentType: 'application/json', 
        beforeSend: function(xhr, settings){
          xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        success: function (response) {
          $("#filedetails").html(response.content)
          
          if(Object.keys(response.json).length === 0){
            $("#prompt-json-conversation").hide()
          }else{
            $("#prompt-json-conversation").show().addClass("btn-outline-success")
          }
          if(response.state == "warning"){
            $.toast({heading: "Info", text: "Le résumé du document n'existe pas, lancer la procédure dans insights.", position: toastPosition, icon: response.state, stack: true,hideAfter: 7000 })
          
          }else{
            $.toast({heading: "Info", text: "Le résumé du document vectorisé est affiché dans insights.", position: toastPosition, icon: response.state, stack: true,hideAfter: 7000 })
          
          }

          
          json_map = "/sharepoint/"+analyse_courante.username+"/"+analyse_courante.analyse+"/"+analyse_courante.entries[0]+".map.json"
          
          // Requête AJAX pour récupérer le JSON
          $.ajax({
            url: json_map,                // URL construite dynamiquement
            method: 'GET',                // Méthode HTTP GET
            dataType: 'json',             // Type de données attendues
            beforeSend: function(xhr, settings){
              xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            },
            success: function(response) { // Callback en cas de succès
                console.log("Données récupérées avec succès :", response.conversation[0].description);
                // Traitez les données ici
                
                plot_response(response.conversation[0].description)
            },
            error: function(xhr, status, error) { // Callback en cas d'erreur
                console.warn("Map : Erreur lors de la récupération des données", error);
            }
          });

          console.log(response);
        },
        error: function () {
        }
      });
    }
    $('#viewer-showdetails').click(function(){
      $(this).toggleClass("btn-info")
      
    });
    

    // liste les dossiers d'analyses de l'utilisateur
    function explorer_analyses(){
      $.ajax({
        url: chatapp_ajax_analyses ,
        type: 'GET',
        beforeSend: function(){
        },
        success: function(response) {
          analyse_courante.username = response.username
          explorerPopulate("explorer_analyses",response)
        },
        error: function() {
        }
      });
    }
    // initialisation de la iste des analyse au chargement de la page
    explorer_analyses()

    
    $("#btn_modal_open_delete_analyse").click(function () {
      if(analyse_courante.analyse==""){
        $.toast({
          heading: "Upload de fichiers",
          text: "Choisir le dossier d'analyse à supprimer",
          position: 'top-left',
          icon: 'warning', // Type of toast icon
          stack: false
        })
        return false
      }else{
        var confirmation = confirm("Êtes-vous sûr de vouloir supprimer ce dossier d'analyse et son contenu ?");
        if (confirmation) {
          $.ajax({
            url: chatapp_ajax_delete_analyse,
            type: 'POST',
            data: JSON.stringify(analyse_courante), 
            contentType: 'application/json', 
            beforeSend: function(xhr, settings){
              xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
            },
            success: function (response) {
                explorerPopulate("explorer_analyses",response)
                explorerEmpty("explorer_fiches")
                console.log(response);
            },
            error: function () {
            }
          });
        }else{
          console.log("opération annulée : chatapp_ajax_delete_analyse")
        }
      }
      
    });

    $("#btn_modal_open_upload").click(function () {
      if(analyse_courante.analyse==""){
        $.toast({
          heading: "Upload de fichiers",
          text: "Choisir un dossier d'analyse",
          position: 'top-left',
          icon: 'error', // Type of toast icon
          stack: false
        })
        return false
      }
      $("#span_upload_dir").html("Dossier d'Analyse <b class='text-info'>" + analyse_courante.analyse+"</b>");
      $("#modal_upload_files").modal('show');
    });


    $("#btn_fusion_pdf").click(function () {
      console.log("btn_fusion_pdf", analyse_courante)
      
      $.ajax({
        url: chatapp_ajax_fusion_pdf,
        type: 'POST',
        data:analyse_courante,
        beforeSend: function(xhr, settings){
          xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        success: function(response) {
          console.log(response)
          explorerPopulate("explorer_fiches",response)
        },
        error: function() {
        }
      });
    });
    $("#chroma_reset").click(function () {
      console.log("chroma_reset", analyse_courante)
      
      $.ajax({
        url: chroma_reset,
        type: 'POST',
        data:analyse_courante,
        beforeSend: function(xhr, settings){
          xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        success: function(response) {
          console.log(response)
          $.toast({heading: "Info",text:response.message})
        },
        error: function() {
        }
      });
    });
    

    $('#upload-form').submit(function (e) {
        var form = $(this)
        e.preventDefault();
        var formData = new FormData(this);
        formData.append("analyse",analyse_courante.analyse)
        $.ajax({
            url: chatapp_upload, 
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
              form[0].reset()
              explorerPopulate("explorer_fiches",response)
              $("#modal_upload_files").modal('hide');
            },
            error: function (error) {
              console.log(error);
            }
        });
    });

    $("#btn_modal_open_new_analyse").click(function(){
      $("#modal_new_analyse").modal('show');
    });
    

    $('#new-analyse-form').submit(function (e) {
      var form = $(this)
      e.preventDefault();
      var new_analyse_name = $("#new_analyse_name").val();
      if(new_analyse_name==""){return false} 
      $.ajax({
          type: "POST",
          url: chatapp_ajax_new_analyse,
          data: JSON.stringify({'analyse': new_analyse_name}),
          contentType: 'application/json',
          beforeSend: function(xhr, settings){
            xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
          },
          success: function (response) {
            form[0].reset()
            explorerPopulate("explorer_analyses",response)
            $("#modal_new_analyse").modal('hide');

          },
          error: function (error) {
              console.log(error);
          }
      });
    });

    
    
    
    // liste les dossiers d'analyses de l'utilisateur
    function chatapp_ajax_set_analyse(analyse){
      analyse_courante.analyse = analyse
      analyse_courante.entries=[]
      $.ajax({
        url: chatapp_ajax_set_analyse_url,
        type: 'POST',
        data:analyse_courante,
        beforeSend: function(xhr, settings){
          xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        },
        success: function(response) {
          explorerPopulate("explorer_fiches",response)
        },
        error: function() {
        }
      });
    }

    



});