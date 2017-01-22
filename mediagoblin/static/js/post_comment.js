/**
 * GNU MediaGoblin -- federated, autonomous media hosting
 * Copyright (C) 2011, 2012 MediaGoblin contributors.  See AUTHORS.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

$(document).ready(function(){
    $(function() {
        // Hide this button if script is enabled
        $('.form_submit_buttons').find('input').hide();

        // Include this link if script is enabled
        $('.form_submit_buttons').append(
            '<a class="button_action" id="post_comment" type="button">' +
            'Add this comment </a>');

        $('#post_comment').click(function() {
            $.ajax({
                url: $('#postCommentURL').val(),
                data: $('#form_comment').serialize(),
                type: 'POST',
                success: function(response) {
                    var message = $(response).find('.mediagoblin_messages');
                    var commentsInResponse = $($(response).find('.media_comments')).find('li');
                    var commentsInPage = $('.media_comments').find('ul');
                    
                    // Post the message
                    message.css({"position":"fixed", "top":"50px", "width":"100%"});
                    $('body').append(message);
                    message.delay(1500).fadeOut();

                    // Checking if there is new comment
                    if(commentsInResponse.length != $(commentsInPage).find('li').length) {
                        // Post comment and scroll down to it
                        var newComment = commentsInResponse[commentsInResponse.length - 1];
                        $('#form_comment').fadeOut('fast');
                        $('#button_addcomment').fadeIn('fast');
                        $('#comment_preview').replaceWith("<div id=comment_preview></div>");
                        $(commentsInPage).append(newComment);
                        $('html, body').animate({
                            scrollTop: $(newComment).offset().top
                        }, 1000);
                    }
                },
                error: function(error) {
                    console.log(error);
                }
            });
        });
    });
});