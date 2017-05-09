/**
 * Created by zss
 */
$(document).ready(function(){
    $("#csshub-loading").hide();
    $("#submitQuestion").click(function(){
            var question = $("#inputquestion").val();
            console.log(question)
            $("#csshub-loading").show();
            $("#answer").hide();
            $.ajax({method:"GET",url:"/ajax_answer/",data:{"question":question},dataType:"json",success:function(data){
						$("#csshub-loading").hide();
						if(data.length > 0){  //返回的数据不能为空
						    $.each(data,function(index,obj){
						        if(index == 0){

						            /*
						           // 1. 返回的是unicode字符编码，使用eval()将unicode转换
						            var answer = "<p>回答：" + eval(obj.content) +"</p>"
                                    $("#answer").html(answer);
                                    */
						            //2. 返回的是utf-8字符编码，不用转换
						            var answer = "<p>回答：" + obj.content +"</p>"
                                    $("#answer").html(answer);
						        }
						    })
						}else{
							$("#answer").html("<p>服务异常，请稍后再试！</p>");
						}
						$("#answer").show();
                         },error: function(XMLHttpRequest, textStatus, errorThrown) {
                         console.log(XMLHttpRequest.status);
                         console.log(XMLHttpRequest.readyState);
                         console.log(textStatus);
            }})

    })
})



