$(document).ready(function(){if($(document).find('.searchable_content').length!=0){$('#searcher').keyup(find_item);}
else{$('#searcher').hide();}});function find_item(){var searching_for=$('#searcher').val().toLowerCase().trim();var search_for_list=searching_for.split(",");var problem_list=$('.item-list').children();for(var index=0;index<problem_list.length;index++){var word_counter=0;var tag_counter=0;$(problem_list[index]).hide();if(searching_for==""){$(problem_list[index]).show();}
else{var empty_word=false;for(var word_index=0;word_index<search_for_list.length;word_index++){var word=search_for_list[word_index].trim();if(word==""){empty_word=true;tag_counter++;}
else{if($(problem_list[index]).find('.searchable_content').text().toLowerCase().indexOf(word)!=-1){word_counter++;}
var current_tags=$(problem_list[index]).find('.tags');var tag_flag=false;for(var tag_index=0;tag_index<current_tags.length;tag_index++){if($(current_tags[tag_index]).text().toLowerCase().indexOf(word)!=-1){tag_flag=true;}}
if(tag_flag){tag_counter++;}}}
if(empty_word){word_counter++;}
if(tag_counter==search_for_list.length){$(problem_list[index]).show();}
else if(word_counter==search_for_list.length){$(problem_list[index]).show();}}}}