# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QuickOSM
 A QGIS plugin
 OSM Overpass API frontend
                             -------------------
        begin                : 2014-06-11
        copyright            : (C) 2014 by 3Liz
        email                : info at 3liz dot com
        contributor          : Etienne Trimaille
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtGui import QTextCharFormat, QSyntaxHighlighter, QColor, QFont
from PyQt4.QtCore import Qt, QRegExp


class XMLHighlighter(QSyntaxHighlighter):

    def __init__(self, parent=None):
        super(XMLHighlighter, self).__init__(parent)

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(Qt.darkMagenta)

        keyword_patterns = [
            "\\b?xml\\b", "/>", ">", "<",
            ";", "\[", "\]", "\(", "\)"
        ]

        self.highlightingRules = [(QRegExp(pattern), keyword_format)
                                  for pattern in keyword_patterns]

        xml_element_format = QTextCharFormat()
        xml_element_format.setForeground(QColor("#117700"))
        self.highlightingRules.append(
            (QRegExp("\\b[A-Za-z0-9_\-]+(?=[\s/>])"), xml_element_format))

        xml_attribute_format = QTextCharFormat()
        xml_attribute_format.setFontItalic(True)
        xml_attribute_format.setForeground(QColor("#2020D2"))
        self.highlightingRules.append(
            (QRegExp("\\b[A-Za-z0-9_]+(?=\\=)"), xml_attribute_format))

        oql_attribute_format = QTextCharFormat()
        oql_attribute_format.setFontItalic(True)
        oql_attribute_format.setForeground(QColor("#2020D2"))
        self.highlightingRules.append(
            (QRegExp("[A-Za-z0-9_]+(?=:)"), oql_attribute_format))

        self.value_format = QTextCharFormat()
        self.value_format.setForeground(Qt.red)

        self.value_start_expression = QRegExp("\"")
        self.value_end_expression = QRegExp("\"(?=[\s></])")

        xml_single_line_comment_format = QTextCharFormat()
        xml_single_line_comment_format.setForeground(Qt.gray)
        self.highlightingRules.append(
            (QRegExp("<!--[^\n]*-->"), xml_single_line_comment_format))

        oql_single_line_comment_format = QTextCharFormat()
        oql_single_line_comment_format.setForeground(Qt.gray)
        self.highlightingRules.append(
            (QRegExp("//[^\n]*"), oql_single_line_comment_format))

        # Multi lines comment
        self.oql_start_comment = QRegExp("\/\*")
        self.oql_end_comment = QRegExp('\*\/')

        overpass = QTextCharFormat()
        overpass.setFontItalic(True)
        overpass.setFontWeight(QFont.Bold)
        overpass.setForeground(QColor("#FF7C00"))
        self.highlightingRules.append(
            (QRegExp("\{\{[A-Za-z0-9:, ]*\}\}"), overpass))

    def match_multiline(self, text, start_delimiter, end_delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = start_delimiter.indexIn(text)
            # Move past this match
            add = start_delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = end_delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + end_delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = end_delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

    def highlightBlock(self, text):
        # for every pattern
        for pattern, char_format in self.highlightingRules:

            # Create a regular expression from the retrieved pattern
            expression = QRegExp(pattern)

            # Check what index that expression occurs at with the ENTIRE text
            index = expression.indexIn(text)

            # While the index is greater than 0
            while index >= 0:

                # Get the length of how long the expression is true,
                # set the format from the start to the length with
                # the text format
                length = expression.matchedLength()
                self.setFormat(index, length, char_format)

                # Set index to where the expression ends in the text
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.value_start_expression.indexIn(text)

        while start_index >= 0:
            end_index = self.value_end_expression.indexIn(text, start_index)

            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = \
                    end_index - start_index + \
                    self.value_end_expression.matchedLength()

            self.setFormat(start_index, comment_length, self.value_format)

            start_index = self.value_start_expression.indexIn(
                text, start_index + comment_length)

        # Do multi-line strings
        self.match_multiline(
            text,
            self.oql_start_comment,
            self.oql_end_comment,
            1,
            Qt.gray)

