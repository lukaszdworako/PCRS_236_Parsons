function create_history_code_mirror(language,version,location){hcm=history_code_mirror(language,version,$('#'+location),$('#'+location).text(),true);if(!(location in cmh_list)){cmh_list[location]=hcm;}}
function history_code_mirror(language,version,location,value,lock){var mode;if(language=='python'){mode={name:language,version:version,singleLineStringErrors:false}}
else if(language=='sql'){mode='text/x-plsql';}
else if(language=='ra'){mode='text/ra';}
else if(language=='c'){mode='text/x-csrc';}
historyCodeMirror=CodeMirror(function(elt){$(location).replaceWith(elt);},{mode:mode,theme:user_theme,value:value,lineNumbers:'True',indentUnit:4,readOnly:lock,lineWrapping:'True',flattenSpans:'False'});return historyCodeMirror;}
var cmh_list={};var language="c";var problem_id="2";var visualizer=null;var happyFace=$('<img id="dynamic">').attr({src:'/static/problems/img/yellow-happy-face.png',alt:'Smiley Face',height:"36",width:"36"});var sadFace=$('<img id="dynamic">').attr({src:'/static/problems/img/red-sad-face.jpg',alt:'Sad Face',height:"36",width:"36"});var happyFaceURL='/static/problems/img/yellow-happy-face.png';var sadFaceURL='/static/problems/img/red-sad-face.jpg';var dURL="/static/problems/img/download-icon.png";function delay_refresh_cm(key){setTimeout(function(){refresh_cm(key)},1);}
function refresh_cm(key){cmh_list[key].refresh();}
function get_problem_type_and_id(div_id){return{type:div_id.split("-")[0],pk:div_id.split("-")[1]};}
function update_marks(div_id,score,max_score){var side_bar=$('.pcrs-sidenav').find('#sb_'+div_id);var new_title=$('#'+div_id).find(".widget_title")[0].firstChild.data.trim();var problem=get_problem_type_and_id(div_id);if(score==max_score){$('#'+div_id).find(".widget_mark").empty();$('#'+div_id).find(".widget_mark").append($('<i/>',{class:"green-checkmark-icon"}));side_bar.removeClass();side_bar.addClass("problem-complete");new_title+=" : Complete";}
else{$('#'+div_id).find(".widget_mark").find('sup').text(score);$('#'+div_id).find(".widget_mark").find('sub').text(max_score);new_title+=" : "+score+" / "+max_score;side_bar.removeClass("problem-not-attempted")
side_bar.addClass("problem-attempted");}
window.dispatchEvent(new CustomEvent('statusUpdate',{detail:{id:problem.type+"-"+problem.pk,problem:{problem_type:problem.type,pk:problem.pk},status:{attempted:true,completed:score==max_score},score:score}}));side_bar.prop('title',new_title);}
var testcases=null;var error_msg=null;var code_problem_id=-1;var myCodeMirrors={};var cmh_list={};var debugger_id="";var debugger_index=0;var last_stepped_line_debugger=0;function bindDebugButton(buttonId){$('#'+buttonId).bind('click',function(){var testcaseCode=$('#tcase_'+buttonId).find(".expression_div").text();setTimeout(function(){prepareVisualizer("debug",testcaseCode,buttonId)},250);});}
function prepareVisualizer(option,testcaseCode,buttonId){var key=buttonId.split("_")[0];var problemId=key.split("-")[1];var newCode=myCodeMirrors[key].getValue()+"\n";if(language=='python'){newCode+=(option=="viz")?myCodeMirrors[key].getValue():testcaseCode;}
getVisualizerComponents(newCode,testcaseCode,problemId);}
function getVisualizerComponents(newCode,testcaseCode,problemId){var postParams={language:language,user_script:newCode,test_case:testcaseCode,problemId:problemId};executeGenericVisualizer("gen_execution_trace_params",postParams);$.post(root+'/problems/'+language+'/visualizer-details',postParams,function(data){executeGenericVisualizer("create_visualizer",data,newCode);},"json").fail(function(jqXHR,textStatus,errorThrown){console.log(textStatus);});}
function getHistory(div_id){var postParams={csrftoken:csrftoken};var problem_path="";check_language(div_id);if(language=='python'){problem_path=root+'/problems/python/'+div_id.split("-")[1]+'/history';}
else if(language=='c'){problem_path=root+'/problems/c/'+div_id.split("-")[1]+'/history';}
else if(language=='sql'){problem_path=root+'/problems/sql/'+div_id.split("-")[1]+'/history';}
else if(language=='ra'){problem_path=root+'/problems/ra/'+div_id.split("-")[1]+'/history';}
$.post(problem_path,postParams,function(data){show_history(data,div_id);},'json').fail(function(jqXHR,textStatus,errorThrown){console.log(textStatus);});}
function add_history_entry(data,div_id,flag){var sub_time=new Date(data['sub_time']);var panel_class="pcrs-panel-default";var star_text="";sub_time=create_timestamp(sub_time);if(data['past_dead_line']){panel_class="pcrs-panel-warning";sub_time=sub_time+" Submitted after the deadline";}
if(data['best']&&!data['past_dead_line']){panel_class="pcrs-panel-star";star_text='<icon style="font-size:1.2em" class="star-icon" title="Latest Best Submission"> </icon>';$('#'+div_id).find('#history_accordion').find(".star-icon").remove();$('#'+div_id).find('#history_accordion').find(".pcrs-panel-star").addClass("pcrs-panel-default").removeClass("pcrs-panel-star");}
var entry=$('<div/>',{class:panel_class});var header1=$('<div/>',{class:"pcrs-panel-heading"});var header2=$('<h4/>',{class:"pcrs-panel-title"});var header4=$('<td/>',{html:"<span class='pull-right'> "+star_text+" "
+"<sup class='h_score'>"+data['score']+"</sup>"
+" / "
+"<sub class='h_score'>"+data['out_of']+"</sub>"
+"</span>"});var header3=$('<a/>',{'data-toggle':"collapse",'data-parent':"#history_accordion",href:"#collapse_"+data['sub_pk'],onclick:"delay_refresh_cm('history_mirror_"
+data['problem_pk']
+"_"
+data['sub_pk']
+"')",html:sub_time+header4.html()});var cont1=$('<div/>',{class:"pcrs-panel-collapse collapse",id:"collapse_"+data['sub_pk']});var cont2=$('<div/>',{id:"history_mirror_"
+data['problem_pk']
+"_"
+data['sub_pk'],html:data['submission']});cont2.html=cont2.text(data['submission']).html();var cont3=$('<ul/>',{class:"pcrs-list-group"});for(var num=0;num<data['tests'].length;num++){var lc="";var ic="";var test_msg="";if(data['tests'][num]['passed']){lc="testcase-success";ic="<icon class='ok-icon'> </icon>";}
else{lc="testcase-fail";ic="<icon class='remove-icon'> </icon>";}
if(data['tests'][num]['visible']){test_msg=" "+data['tests'][num]['input']+" -> "+data['tests'][num]['output'];}
else{if(data['tests'][num]['description']==""){test_msg=" Hidden Test";}
else{test_msg=" "+data['tests'][num]['description'];}}
var cont4=$('<li/>',{class:lc,html:ic+test_msg});cont3.append(cont4);}
header2.append(header3);header1.append(header2);entry.append(header1);cont1.append(cont2);cont1.append(cont3);entry.append(cont1);if(flag==0){$('#'+div_id).find('#history_accordion').append(entry);}
else{$('#'+div_id).find('#history_accordion').prepend(entry);}
check_language(div_id);if(language=="python"){create_history_code_mirror("python",3,"history_mirror_"
+data['problem_pk']
+"_"
+data['sub_pk']);}
else{create_history_code_mirror(language,false,"history_mirror_"
+data['problem_pk']
+"_"
+data['sub_pk']);}}
function show_history(data,div_id){for(var x=0;x<data.length;x++){add_history_entry(data[x],div_id,0);}}
function addHashkey(div_id){var line_count=myCodeMirrors[div_id].lineCount();var code=" ";var wrapClass;var i;for(i=0;i<line_count;i++){wrapClass=myCodeMirrors[div_id].lineInfo(i).wrapClass;if(wrapClass=='CodeMirror-studentline-background')
code+=CryptoJS.SHA1(div_id.split("-")[1]);else
code+=myCodeMirrors[div_id].getLine(i);code+='\n';}
return code.substring(0,code.length-1);}
function handleCMessages(div_id,testcases){$('#'+div_id).find('#c_warning').remove();$('#'+div_id).find('#c_error').remove();var bad_testcase=null;for(var i=0;i<testcases.length;i++){if("exception_type"in testcases[i]){bad_testcase=testcases[i];break;}}
if(bad_testcase!=null){var class_type;if(bad_testcase.exception_type=="warning"){class_type='alert alert-warning';}
else if(bad_testcase.exception_type=="error"){class_type='alert alert-danger';}
$('#'+div_id).find('#alert').before('<div id="c_warning" class="'+class_type+'" style="font-weight: bold">'+bad_testcase.exception+'</div>');}}
function getTestcases(div_id){var clean_code;if(language=='c'){clean_code=addHashkey(div_id);}else{clean_code=myCodeMirrors[div_id].getValue();}
while(clean_code.indexOf('\t')!=-1){clean_code=clean_code.replace('\t',"    ");}
var postParams={csrftoken:csrftoken,submission:clean_code};var call_path="";check_language(div_id);if(language=='python'){call_path=root+'/problems/python/'+div_id.split("-")[1]+'/run'}
else if(language=='c'){call_path=root+'/problems/c/'+div_id.split("-")[1]+'/run'}
else if(language=='sql'){call_path=root+'/problems/sql/'+div_id.split("-")[1]+'/run';}
else if(language=='ra'){call_path=root+'/problems/ra/'+div_id.split("-")[1]+'/run';}
$('#waitingModal').modal('show');$.post(call_path,postParams,function(data){if(data['past_dead_line']){alert("This submission is past the deadline!")
$('#'+div_id).find('#deadline_msg').remove();$('#'+div_id).find('#alert').after('<div id="deadline_msg" class="red-alert">Submitted after the deadline!<div>');}
testcases=data['results'][0];if(data['results'][1]!=null){error_msg=data['results'][1];}
$("#"+div_id).find("#grade-code").show();var score=data['score'];var max_score=data['max_score'];var desider=score==max_score;$('#'+div_id).find('#alert').toggleClass("red-alert",!desider);$('#'+div_id).find('#alert').toggleClass("green-alert",desider);$('#'+div_id).find('#alert').children('icon').toggleClass("remove-icon",!desider);$('#'+div_id).find('#alert').children('icon').toggleClass("ok-icon",desider);if(desider){$('#'+div_id).find('#alert').children('span').text("Your solution is correct!");$('#'+div_id).find('.screen-reader-text').prop('title',"Your solution is correct!");}
else{$('#'+div_id).find('#alert').children('span').text("Your solution passed "+score+" out of "+max_score+" cases!");$('#'+div_id).find('.screen-reader-text').text("Your solution passed "+score+" out of "+max_score+" cases!");}
if(language=='python'){prepareGradingTable(div_id,data['best'],data['past_dead_line'],data['sub_pk'],max_score);}
else if(language=='c'){handleCMessages(div_id,testcases);prepareGradingTable(div_id,data['best'],data['past_dead_line'],data['sub_pk'],max_score);}
else if(language=='sql'){prepareSqlGradingTable(div_id,data['best'],data['past_dead_line'],data['sub_pk'],max_score);}
else if(language=='ra'){prepareSqlGradingTable(div_id,data['best'],data['past_dead_line'],data['sub_pk'],max_score);}
$('#waitingModal').modal('hide');},"json").fail(function(jqXHR,textStatus,errorThrown){$('#waitingModal').modal('hide');console.log(textStatus);});}
function prepareSqlGradingTable(div_id,best,past_dead_line,sub_pk,max_score){var score=0;var tests=[];var table_location=$('#'+div_id).find('#table_location');table_location.empty();if(error_msg!=null){table_location.append("<div class='red-alert'>"+error_msg+"</div>");error_msg=null;}
else{for(var i=0;i<testcases.length;i++){var current_testcase=testcases[i];var main_table=$('<table/>',{id:"gradeMatrix"+current_testcase['testcase'],class:"pcrs-table"});var expected_td=$('<td/>',{class:"table-left"}).append("Expected");var actual_td=$('<td/>',{class:"table-right"}).append("Actual");var left_wrapper=$('<div/>',{class:"sql_table_control"});var right_wrapper;if(current_testcase['visible'])
right_wrapper=$('<div/>',{class:"sql_table_control"});else{right_wrapper=$('<div/>',{class:"sql_table_control_full"});}
var expected_table=$('<table/>',{class:"pcrs-table"});var actual_table=$('<table/>',{class:"pcrs-table"});var expected_entry=$('<tr/>',{class:"pcrs-table-head-row"});var actual_entry=$('<tr/>',{class:"pcrs-table-head-row"});if(current_testcase['passed']){table_location.append("<div class='green-alert'><icon class='ok-icon'>"+"</icon><span> Test Case Passed</span></div>");score++;}
else{table_location.append("<div class='red-alert'><icon class='remove-icon'>"+"</icon><span> Test Case Failed</span></div>");}
if(current_testcase['error']!=null){table_location.append("<div class='red-alert'>"+current_testcase['error']+"</div>");}
else{if(current_testcase['visible']){for(var header=0;header<current_testcase['expected_attrs'].length;header++){expected_entry.append("<td><b>"+current_testcase['expected_attrs'][header]+"</b></td>");}}
else{table_location.append("<div class='blue-alert'>"+"</icon><span> Expected Result is Hidden </span></div>");}
for(var header=0;header<current_testcase['actual_attrs'].length;header++){actual_entry.append("<td><b>"+current_testcase['actual_attrs'][header]+"</b></td>");}
expected_table.append(expected_entry);actual_table.append(actual_entry);expected_table.removeClass("pcrs-table-head-row").addClass("pcrs-table-row");actual_table.removeClass("pcrs-table-head-row").addClass("pcrs-table-row");if(current_testcase['visible']){for(var entry=0;entry<current_testcase['expected'].length;entry++){var entry_class='pcrs-table-row';var test_entry=current_testcase['expected'][entry];if(test_entry['missing']){entry_class="pcrs-table-row-missing";}
var expected_entry=$('<tr/>',{class:entry_class});for(var header=0;header<current_testcase['expected_attrs'].length;header++){expected_entry.append("<td>"+
test_entry[current_testcase['expected_attrs'][header]]+"</td>");}
expected_table.append(expected_entry);}}
for(var entry=0;entry<current_testcase['actual'].length;entry++){var entry_class='pcrs-table-row';var test_entry=current_testcase['actual'][entry];if(test_entry['extra']){entry_class='pcrs-table-row-extra';}
else if(test_entry['out_of_order']){entry_class='pcrs-table-row-order';}
var actual_entry=$('<tr/>',{class:entry_class});for(var header=0;header<current_testcase['actual_attrs'].length;header++){actual_entry.append("<td>"+
test_entry[current_testcase['actual_attrs'][header]]+"</td>");}
actual_table.append(actual_entry);}
if(current_testcase['visible']){left_wrapper.append(expected_table);expected_td.append(left_wrapper);main_table.append(expected_td);}
right_wrapper.append(actual_table);actual_td.append(right_wrapper);main_table.append(actual_td);table_location.append(main_table);}}}
var data={'sub_time':new Date(),'submission':myCodeMirrors[div_id].getValue(),'score':score,'best':best,'past_dead_line':past_dead_line,'problem_pk':div_id.split("-")[1],'sub_pk':sub_pk,'out_of':max_score,'tests':table_location};if(best&&!data['past_dead_line']){update_marks(div_id,score,max_score);}
var flag=($('#'+div_id).find('#history_accordion').children().length!=0);add_history_entry(data,div_id,flag);}
function prepareGradingTable(div_id,best,past_dead_line,sub_pk,max_score){var gradingTable=$("#"+div_id).find("#gradeMatrix");var score=0;var tests=[];if(error_msg!=null){gradingTable.append("<div class='red-alert'>"+error_msg+"</div>");error_msg=null;}
else{for(var i=0;i<testcases.length;i++){var current_testcase=testcases[i];var description=current_testcase.test_desc;var passed=current_testcase.passed_test;var testcaseInput=current_testcase.test_input;var testcaseOutput=current_testcase.expected_output;var result=create_output(current_testcase.test_val);var cleaner=$(gradingTable).find('#tcase_'+div_id+'_'+i);if(description==""){description="No Description Provided"}
if(cleaner){cleaner.remove();}
var newRow=$('<tr class="pcrs-table-row" id="tcase_'+div_id+'_'+i+'"></tr>');gradingTable.append(newRow);if(language!='c'&&"exception"in current_testcase){newRow.append('<th class="red-alert" colspan="12" style="width:100%;">'+
current_testcase.exception+'</th>');}
else if(!(language=='c'&&"exception"in current_testcase&&current_testcase.exception_type=="error")){if(testcaseInput!=null){newRow.append('<td class="description">'+
description+'</td>');newRow.append('<td class="expression"><div class="expression_div">'+
testcaseInput+'</div></td>');newRow.append('<td class="expected"><div class="ptd"><div id="exp_test_val" class="ExecutionVisualizer"></div></td></div>');}
else{newRow.append('<td class="description">'+description+'</td>');newRow.append('<td class="expression">'+"Hidden Test"+'</td>');newRow.append('<td class="expected">'+"Hidden Result"+'</td>');}
newRow.append('<td class="result"><div class="ptd"><div id="current_testcase'+i+'" class="ExecutionVisualizer">'+''+'</div></div></td>');renderData_ignoreID(current_testcase.test_val,$('#current_testcase'+i));$('#current_testcase'+i).attr('id',"");renderData_ignoreID(current_testcase.exp_test_val,$('#exp_test_val'));$('#exp_test_val').attr('id',"");newRow.append('<td class="passed"></td>');var pass_status="";if(passed){var smFace=happyFace;score+=1;pass_status="passed";}
else{var smFace=sadFace;pass_status="failed";}
$("#"+div_id).find('#tcase_'+div_id+'_'+i+' td.passed').html(smFace.clone());if(testcaseInput!=null){newRow.append('<td class="debug"><button id="'+
div_id+"_"+i+'" class="debugBtn" type="button"'+' >Trace</button></td>');bindDebugButton(div_id+"_"+i);}
else{newRow.append('<td class="debug"></td>')}
newRow.append('<a class="at" href="">This testcase has '+pass_status+'. Expected: '+
testcaseOutput+'. Result: '+result+'</a>');}
var test={'visible':testcaseInput!=null,'input':testcaseInput,'output':testcaseOutput,'passed':passed,'description':description};tests.push(test);}}
var data={'sub_time':new Date(),'submission':myCodeMirrors[div_id].getValue(),'score':score,'best':best,'past_dead_line':past_dead_line,'problem_pk':div_id.split("-")[1],'sub_pk':sub_pk,'out_of':max_score,'tests':tests};if(best&&!data['past_dead_line']){update_marks(div_id,score,max_score);}
var flag=($('#'+div_id).find('#history_accordion').children().length!=0);add_history_entry(data,div_id,flag);}
function create_timestamp(datetime){var month_names=["January","February","March","April","May","June","July","August","September","October","November","December"];var day=datetime.getDate();var month=month_names[datetime.getMonth()];var year=datetime.getFullYear();var hour=datetime.getHours();var minute=datetime.getMinutes();if(String(minute).length==1){minute="0"+minute}
if(hour>12){hour-=12;cycle="p.m.";}
else{cycle="a.m.";}
var formated_datetime=month+" "+day+", "+year+", "+hour+":"+minute+" "+cycle
return formated_datetime;}
function create_output(input){brakets_o={"list":"[","tuple":"(","dict":"{"};brakets_c={"list":"]","tuple":")","dict":"}"};if(language=='c'){return input;}
else if(input.length==2){return create_output(input[0])+":"+create_output(input[1]);}
else if(input[0]=="list"||input[0]=="tuple"||input[0]=="dict"){var output=brakets_o[input[0]];for(var o_index=2;o_index<input.length;o_index++){output+=create_output(input[o_index]);if(o_index!=input.length-1){output+=", "}}
output+=brakets_c[input[0]];return output}
else if(input[0]=="string"){return"'"+input[2]+"'";}
else if(input[0]=="float"){if(String(input[2]).indexOf(".")>-1){return input[2]}
else{return input[2]+".0"}}
else{return input[2]}}
function check_language(container){if(container.indexOf("c")>-1){language='c';}
else if(container.indexOf("python")>-1){language='python';}
else if(container.indexOf("sql")>-1){language='sql';}
else if(container.indexOf("ra")>-1){language='ra';}
else{language='';}}
function escapeRegExp(string){return string.replace(/([.*+?^=!:${}()|\[\]\/\\])/g,"\\$1");}
function replaceAll(find,replace,string){return string.replace(new RegExp(escapeRegExp(find),'g'),replace);}
function removeTags(source_code){var lines=source_code.split("\n");var line;var blocked_open=0;var blocked_list=[];var student_code_list=[];var tag_num=0;source_code="";for(var i=0;i<lines.length;i++){line=lines[i];if((line.split("[blocked]").length-1)>0){blocked_list.push({"highlight":true,"start":i+1-tag_num,"end":0});blocked_open+=1;tag_num+=1;}
else if((line.split("[/blocked]").length-1)>0){tag_num+=1;blocked_list[blocked_open-1].end=i+1-tag_num;}
else if((line.split("[student_code]").length-1)>0){student_code_list.push({"highlight":false,"start":i+1-tag_num,"end":i+1-tag_num});source_code+='//Implementation start'+'\n';}
else if((line.split("[/student_code]").length-1)>0){student_code_list.push({"highlight":false,"start":i+1-tag_num,"end":i+1-tag_num});source_code+='//Implementation end'+'\n';}else{source_code+=lines[i]+'\n';}}
var tag_list;source_code=source_code.substring(0,source_code.length-1);tag_list=blocked_list.concat(student_code_list);return{source_code:source_code,tag_list:tag_list};}
function blockInput(editor_id){var line_num=myCodeMirrors[editor_id].getCursor().line;var line_count;var wrapClass=myCodeMirrors[editor_id].lineInfo(line_num).wrapClass;if(wrapClass=='CodeMirror-studentline-background'||wrapClass=='CodeMirror-activeline-background')
{line_count=myCodeMirrors[editor_id].lineCount();for(var i=0;i<line_count;i++){wrapClass=myCodeMirrors[editor_id].lineInfo(i).wrapClass;if(wrapClass!='CodeMirror-studentline-background'&&wrapClass!='CodeMirror-activeline-background'){myCodeMirrors[editor_id].setCursor(i,0);return true;}}
myCodeMirrors[editor_id].replaceRange("\n",CodeMirror.Pos(myCodeMirrors[editor_id].lastLine()));myCodeMirrors[editor_id].setCursor(myCodeMirrors[editor_id].lineCount(),0);}}
function highlightCode(editor_id,tag_list){myCodeMirrors[editor_id].on("cursorActivity",function(){blockInput(editor_id);});var first_line=myCodeMirrors[editor_id].firstLine();var last_line=myCodeMirrors[editor_id].lastLine();for(var i=first_line;i<=last_line;i++){for(var j=0;j<tag_list.length;j++){if(tag_list[j].start<=i+1&&tag_list[j].end>=i+1){if(tag_list[j].highlight==true)
myCodeMirrors[editor_id].addLineClass(i,'','CodeMirror-activeline-background');else if(tag_list[j].highlight==false)
myCodeMirrors[editor_id].addLineClass(i,'','CodeMirror-studentline-background');break;}}}}
$(document).ready(function(){var all_wrappers=$('.code-mirror-wrapper');for(var x=0;x<all_wrappers.length;x++){$(all_wrappers[x]).children('#grade-code').hide();check_language(all_wrappers[x].id);if(language=="python"){myCodeMirrors[all_wrappers[x].id]=history_code_mirror("python",3,$(all_wrappers[x]).find("#div_id_submission"),$(all_wrappers[x]).find('#div_id_submission').text(),false);}
else if(language=="c"){var codeObj=removeTags($(all_wrappers[x]).find('#div_id_submission').text());myCodeMirrors[all_wrappers[x].id]=history_code_mirror(language,'text/x-csrc',$(all_wrappers[x]).find("#div_id_submission"),codeObj.source_code,false);debugger_id=all_wrappers[x].id+1;myCodeMirrors[debugger_id]=history_code_mirror(language,'text/x-csrc',$("#id_preview_code_debugger"),codeObj.source_code,false);highlightCode(all_wrappers[x].id,codeObj.tag_list);}
else if(language=="sql"){myCodeMirrors[all_wrappers[x].id]=history_code_mirror(language,'text/x-sql',$(all_wrappers[x]).find("#div_id_submission"),$(all_wrappers[x]).find('#div_id_submission').text(),false);}
else if(language=="ra"){myCodeMirrors[all_wrappers[x].id]=history_code_mirror(language,'text/x-sql',$(all_wrappers[x]).find("#div_id_submission"),$(all_wrappers[x]).find('#div_id_submission').text(),false);}
$(all_wrappers[x]).find('#submit-id-submit').click(function(event){event.preventDefault();var div_id=$(this).parents('.code-mirror-wrapper')[0].id;if(myCodeMirrors[div_id].getValue()==''){alert('There is no code to submit.');}
else{getTestcases(div_id);}});$(all_wrappers[x]).find("[name='history']").one("click",(function(){var div_id=$(this).parents('.code-mirror-wrapper')[0].id;getHistory(div_id);}));}
$(window).bind("load",function(){$('.CodeMirror').each(function(i,el){el.CodeMirror.refresh();});});});function executeGenericVisualizer(option,data,newCode){var supportedVisualization=['python','c'];if(visualizationSupported()){if(language=='python'){return executePythonVisualizer(option,data);}
else if(language=='c'){return executeCVisualizer(option,data,newCode);}}else{alert("No support for visualization available!");return null;}
function visualizationSupported(){return $.inArray(language,supportedVisualization)>-1;}
function executePythonVisualizer(option,data){switch(option){case"create_visualizer":createVisualizer(data);break;case"gen_execution_trace_params":getExecutionTraceParams(data);break;case"render_data":codeStr=data.codeStr;targetElement=data.targetElement;renderVal(codeStr,targetElement);break;default:return"option not supported";}
function createVisualizer(data){if(errorsInTracePy(data)){changeView("edit-code");}
else{visualizer=createVisualizerPy(data);visualizer.updateOutput();}}
function errorsInTracePy(data){var errors_caught=false;if(data.exception){alert(data.exception);errors_caught=true;}
else{trace=data.trace;if(trace.length==0){var errorLineNo=trace[0].line-1;if(errorLineNo!==undefined){mainCodeMirror.focus();mainCodeMirror.setCursor(errorLineNo,0);mainCodeMirror.setLineClass(errorLineNo,null,'errorLine');mainCodeMirror.setOption('onChange',function(){mainCodeMirror.setLineClass(errorLineNo,null,null);mainCodeMirror.setOption('onChange',null);});}
alert("Syntax error, cannot visualize code execution");errors_caught=true;}
else if(trace[trace.length-1].exception_msg){alert(trace[trace.length-1].exception_msg);errors_caught=true;}
else if(!trace){alert("Unknown error.");errors_caught=true;}}
return errors_caught;}
function createVisualizerPy(data){var pyVisualizer=new ExecutionVisualizer('visualize-code',data,{startingInstruction:0,updateOutputCallback:function(){$('#urlOutput,#embedCodeOutput').val('');},disableHeapNesting:('true'=='true'),drawParentPointers:('true'=='true'),textualMemoryLabels:('true'=='true'),});$(document).keydown(function(k){if(k.keyCode==37){if(pyVisualizer.stepBack()){k.preventDefault();keyStuckDown=true;}}
else if(k.keyCode==39){if(pyVisualizer.stepForward()){k.preventDefault();keyStuckDown=true;}}});$(document).keyup(function(k){keyStuckDown=false;});$(document).scrollTop(0);return pyVisualizer;}
function getExecutionTraceParams(initPostParams){cumulative_mode='false';heap_primitives='true';initPostParams.add_params=JSON.stringify({cumulative_mode:cumulative_mode,heap_primitives:heap_primitives});}
function renderVal(codeStr,targetElement){targetElement.empty();renderData_ignoreID(codeStr,targetElement);}}
function executeCVisualizer(option,data,newCode){switch(option){case"create_visualizer":createVisualizer(data,newCode);break;case"gen_execution_trace_params":getExecutionTraceParams(data);break;case"render_data":codeStr=data.codeStr;targetElement=data.targetElement;renderVal(codeStr,targetElement);break;default:return"option not supported";}
function createVisualizer(data,newCode){myCodeMirrors[debugger_id].setValue(newCode);$('#visualizerModal').on('shown.bs.modal',function(){myCodeMirrors[debugger_id].refresh();});update_debugger_table(data);$('#visualizerModal').modal('show');$('#previous_debugger').bind('click',{data:data},function(){if(debugger_index>=1){debugger_index--;}
update_debugger_table(data);});$('#next_debugger').bind('click',{data:data},function(){if(typeof data[debugger_index]!='undefined'){debugger_index++;update_debugger_table(data);}});$('#reset_debugger').bind('click',{data:data},function(){debugger_index=0;update_debugger_table(data);});}
function update_debugger_table(data){$('#debugger_table').empty();myCodeMirrors[debugger_id].removeLineClass(last_stepped_line_debugger,'','CodeMirror-activeline-background');for(var i=0;i<data[debugger_index].length;i++){myCodeMirrors[debugger_id].addLineClass(parseInt(data[debugger_index][i][0]-1),'','CodeMirror-activeline-background');$('#debugger_table').append('<tr>'+'<th class="text-nowrap" scope="row">'+data[debugger_index][i][4]+'</th>'+'<td>'+data[debugger_index][i][2]+'</td>'+'<td>'+data[debugger_index][i][3]+'</td>'+'<td>'+data[debugger_index][i][1]+'</td>'+'</tr>');last_stepped_line_debugger=parseInt(data[debugger_index][i][0]-1);}}
function getExecutionTraceParams(initPostParams){initPostParams.add_params=JSON.stringify({test_case:initPostParams.test_case});}
function renderVal(codeStr,targetElement){targetElement.empty();renderData_ignoreID(codeStr,targetElement);}}}