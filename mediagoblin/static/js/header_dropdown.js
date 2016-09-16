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
  // The header drop-down header panel defaults to open until you explicitly
  // close it. After that, the panel open/closed setting will persist across
  // page loads.

  // Initialise the panel status when page is loaded.
  if (localStorage.getItem("panel_closed")) {
    $("#header_dropdown").hide();
    $(".header_dropdown_up").hide();
  }
  else {
    $(".header_dropdown_down").hide();
  }

  // Toggle and persist the panel status.
  $(".header_dropdown_down, .header_dropdown_up").click(function() {
    if (localStorage.getItem("panel_closed")) {
      localStorage.removeItem("panel_closed");
    }
    else {
      localStorage.setItem("panel_closed", "true");
    }
    $(".header_dropdown_down").toggle();
    $(".header_dropdown_up").toggle();
    $("#header_dropdown").slideToggle();
  });
});
