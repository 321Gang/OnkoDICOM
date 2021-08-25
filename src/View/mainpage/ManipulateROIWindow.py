import pydicom
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QSizePolicy, QPushButton, \
    QLabel, QWidget, QFormLayout

from src.Model import ROI
from src.Model.PatientDictContainer import PatientDictContainer
from src.Model.Worker import Worker
from src.View.mainpage.DicomAxialView import DicomAxialView

from src.Controller.PathHandler import resource_path
import platform


class UIManipulateROIWindow:

    def setup_ui(self, manipulate_roi_window_instance, rois, dataset_rtss, signal_roi_manipulated):

        self.patient_dict_container = PatientDictContainer()
        self.rois = rois
        self.dataset_rtss = dataset_rtss
        self.signal_roi_manipulated = signal_roi_manipulated

        self.roi_names = []
        for roi_id, roi_dict in self.rois.items():
            self.roi_names.append(roi_dict['name'])

        self.single_roi_operation_names = ["Expand", "Contract", "Inner Rind (annulus)", "Outer Rind (annulus)"]
        self.multiple_roi_operation_names = ["Union", "Intersection", "Difference"]
        self.operation_names = self.single_roi_operation_names + self.multiple_roi_operation_names

        self.ROI_name = None  # Selected ROI name
        self.manipulate_roi_window_instance = manipulate_roi_window_instance
        self.ds = None

        self.dicom_view = DicomAxialView(metadata_formatted=True)
        self.dicom_preview = DicomAxialView(metadata_formatted=True)
        self.init_layout()

        QtCore.QMetaObject.connectSlotsByName(manipulate_roi_window_instance)

    def retranslate_ui(self, manipulate_roi_window_instance):
        _translate = QtCore.QCoreApplication.translate
        manipulate_roi_window_instance.setWindowTitle(_translate("ManipulateRoiWindowInstance", "OnkoDICOM - Draw Region Of Interest"))
        self.first_roi_name_label.setText(_translate("FirstROINameLabel", "ROI 1: "))
        self.first_roi_name_dropdown_list.setPlaceholderText("ROI 1")
        self.first_roi_name_dropdown_list.addItems(self.roi_names)
        self.operation_name_label.setText(_translate("OperationNameLabel", "Operation"))
        self.operation_name_dropdown_list.setPlaceholderText("Operation")
        self.operation_name_dropdown_list.addItems(self.operation_names)
        self.second_roi_name_label.setText(_translate("SecondROINameLabel", "ROI 2: "))
        self.second_roi_name_dropdown_list.setPlaceholderText("ROI 2")
        self.second_roi_name_dropdown_list.addItems(self.roi_names)
        self.manipulate_roi_window_instance_draw_button.setText(_translate("ManipulateRoiWindowInstanceDrawButton", "Draw"))
        self.manipulate_roi_window_instance_save_button.setText(_translate("ManipulateRoiWindowInstanceSaveButton", "Save"))
        self.manipulate_roi_window_instance_cancel_button.setText(_translate("ManipulateRoiWindowInstanceCancelButton", "Cancel"))
        self.margin_label.setText(_translate("MarginLabel", "Margin (pixels): "))
        self.new_roi_name_label.setText(_translate("NewROINameLabel", "New ROI Name"))
        self.ROI_view_box_label.setText("ROI")
        self.preview_box_label.setText("Preview")

    def init_layout(self):
        """
        Initialize the layout for the DICOM View tab.
        Add the view widget and the slider in the layout.
        Add the whole container 'tab2_view' as a tab in the main page.
        """

        # Initialise a ManipulateROIWindow
        if platform.system() == 'Darwin':
            self.stylesheet_path = "res/stylesheet.qss"
        else:
            self.stylesheet_path = "res/stylesheet-win-linux.qss"
        stylesheet = open(resource_path(self.stylesheet_path)).read()
        window_icon = QIcon()
        window_icon.addPixmap(QPixmap(resource_path("res/images/icon.ico")), QIcon.Normal, QIcon.Off)
        self.manipulate_roi_window_instance.setObjectName("ManipulateRoiWindowInstance")
        self.manipulate_roi_window_instance.setWindowIcon(window_icon)

        # Creating a form box to hold all buttons and input fields
        self.manipulate_roi_window_input_container_box = QFormLayout()
        self.manipulate_roi_window_input_container_box.setObjectName("ManipulateRoiWindowInputContainerBox")
        self.manipulate_roi_window_input_container_box.setLabelAlignment(Qt.AlignLeft)

        # Create a label for denoting the first ROI name
        self.first_roi_name_label = QLabel()
        self.first_roi_name_label.setObjectName("FirstROINameLabel")
        self.first_roi_name_dropdown_list = QComboBox()
        # Create an dropdown list for ROI name
        self.first_roi_name_dropdown_list.setObjectName("FirstROINameDropdownList")
        self.first_roi_name_dropdown_list.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.first_roi_name_dropdown_list.resize(self.first_roi_name_dropdown_list.sizeHint().width(),
                                                 self.first_roi_name_dropdown_list.sizeHint().height())
        self.manipulate_roi_window_input_container_box.addRow(self.first_roi_name_label,
                                                              self.first_roi_name_dropdown_list)

        # Create a label for denoting the operation
        self.operation_name_label = QLabel()
        self.operation_name_label.setObjectName("OperationNameLabel")
        self.operation_name_dropdown_list = QComboBox()
        # Create an dropdown list for operation name
        self.operation_name_dropdown_list.setObjectName("OperationNameDropdownList")
        self.operation_name_dropdown_list.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.operation_name_dropdown_list.resize(self.operation_name_dropdown_list.sizeHint().width(),
                                                 self.operation_name_dropdown_list.sizeHint().height())
        self.operation_name_dropdown_list.activated.connect(self.operation_changed)
        self.manipulate_roi_window_input_container_box.addRow(self.operation_name_label, self.operation_name_dropdown_list)

        # Create a label for denoting the second ROI name
        self.second_roi_name_label = QLabel()
        self.second_roi_name_label.setObjectName("SecondROINameLabel")
        self.second_roi_name_label.setVisible(False)
        self.second_roi_name_dropdown_list = QComboBox()
        # Create an dropdown list for ROI name
        self.second_roi_name_dropdown_list.setObjectName("SecondROINameDropdownList")
        self.second_roi_name_dropdown_list.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.second_roi_name_dropdown_list.resize(self.second_roi_name_dropdown_list.sizeHint().width(),
                                                  self.second_roi_name_dropdown_list.sizeHint().height())
        self.second_roi_name_dropdown_list.setVisible(False)
        self.manipulate_roi_window_input_container_box.addRow(self.second_roi_name_label,
                                                              self.second_roi_name_dropdown_list)

        # Create a label for denoting the margin
        self.margin_label = QLabel()
        self.margin_label.setObjectName("MarginLabel")
        self.margin_label.setVisible(False)
        # Create input for the new ROI name
        self.margin_line_edit = QLineEdit()
        self.margin_line_edit.setObjectName("MarginInput")
        self.margin_line_edit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.margin_line_edit.resize(self.margin_line_edit.sizeHint().width(),
                                     self.margin_line_edit.sizeHint().height())
        self.margin_line_edit.setVisible(False)
        self.manipulate_roi_window_input_container_box.addRow(self.margin_label, self.margin_line_edit)

        # Create a label for denoting the new ROI name
        self.new_roi_name_label = QLabel()
        self.new_roi_name_label.setObjectName("NewROINameLabel")
        # Create input for the new ROI name
        self.new_roi_name_line_edit = QLineEdit()
        self.new_roi_name_line_edit.setObjectName("NewROINameInput")
        self.new_roi_name_line_edit.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.new_roi_name_line_edit.resize(self.new_roi_name_line_edit.sizeHint().width(),
                                                self.new_roi_name_line_edit.sizeHint().height())
        self.manipulate_roi_window_input_container_box.addRow(self.new_roi_name_label, self.new_roi_name_line_edit)

        # Create a spacer between inputs and buttons
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        spacer.setFocusPolicy(Qt.NoFocus)
        self.manipulate_roi_window_input_container_box.addRow(spacer)

        # Create a draw button
        self.manipulate_roi_window_instance_draw_button = QPushButton()
        self.manipulate_roi_window_instance_draw_button.setObjectName("ManipulateRoiWindowInstanceDrawButton")
        self.manipulate_roi_window_instance_draw_button.setSizePolicy(
            QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum))
        self.manipulate_roi_window_instance_draw_button.resize(
            self.manipulate_roi_window_instance_draw_button.sizeHint().width(),
            self.manipulate_roi_window_instance_draw_button.sizeHint().height())
        self.manipulate_roi_window_instance_draw_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.manipulate_roi_window_instance_draw_button.clicked.connect(self.onDrawButtonClicked)
        self.manipulate_roi_window_input_container_box.addRow(self.manipulate_roi_window_instance_draw_button)

        # Create a horizontal box for saving and cancel the drawing
        self.manipulate_roi_window_cancel_save_box = QHBoxLayout()
        self.manipulate_roi_window_cancel_save_box.setObjectName("ManipulateRoiWindowCancelSaveBox")
        # Create an exit button to cancel the drawing
        # Add a button to go back/exit from the application
        self.manipulate_roi_window_instance_cancel_button = QPushButton()
        self.manipulate_roi_window_instance_cancel_button.setObjectName("ManipulateRoiWindowInstanceCancelButton")
        self.manipulate_roi_window_instance_cancel_button.setSizePolicy(
            QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum))
        self.manipulate_roi_window_instance_cancel_button.resize(
            self.manipulate_roi_window_instance_cancel_button.sizeHint().width(),
            self.manipulate_roi_window_instance_cancel_button.sizeHint().height())
        self.manipulate_roi_window_instance_cancel_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.manipulate_roi_window_instance_cancel_button.clicked.connect(self.onCancelButtonClicked)
        self.manipulate_roi_window_instance_cancel_button.setProperty("QPushButtonClass", "fail-button")
        icon_cancel = QtGui.QIcon()
        icon_cancel.addPixmap(QtGui.QPixmap(resource_path('res/images/btn-icons/cancel_icon.png')))
        self.manipulate_roi_window_instance_cancel_button.setIcon(icon_cancel)
        self.manipulate_roi_window_cancel_save_box.addWidget(self.manipulate_roi_window_instance_cancel_button)
        # Create a save button to save all the changes
        self.manipulate_roi_window_instance_save_button = QPushButton()
        self.manipulate_roi_window_instance_save_button.setObjectName("ManipulateRoiWindowInstanceSaveButton")
        self.manipulate_roi_window_instance_save_button.setSizePolicy(
            QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum))
        self.manipulate_roi_window_instance_save_button.resize(
            self.manipulate_roi_window_instance_save_button.sizeHint().width(),
            self.manipulate_roi_window_instance_save_button.sizeHint().height())
        self.manipulate_roi_window_instance_save_button.setProperty("QPushButtonClass", "success-button")
        icon_save = QtGui.QIcon()
        icon_save.addPixmap(QtGui.QPixmap(resource_path('res/images/btn-icons/save_icon.png')))
        self.manipulate_roi_window_instance_save_button.setIcon(icon_save)
        self.manipulate_roi_window_instance_save_button.clicked.connect(self.onSaveClicked)
        self.manipulate_roi_window_cancel_save_box.addWidget(self.manipulate_roi_window_instance_save_button)
        self.manipulate_roi_window_input_container_box.addRow(self.manipulate_roi_window_cancel_save_box)

        # Creating a horizontal box to hold the ROI view and the preview
        self.manipulate_roi_window_instance_view_box = QHBoxLayout()
        self.manipulate_roi_window_instance_view_box.setObjectName("ManipulateRoiWindowInstanceViewBoxes")
        # Creating the ROI view
        self.ROI_view_box_layout = QVBoxLayout()
        self.ROI_view_box_label = QLabel()
        self.ROI_view_box_layout.addWidget(self.ROI_view_box_label)
        self.ROI_view_box_layout.addWidget(self.dicom_view)
        self.ROI_view_box_widget = QWidget()
        self.ROI_view_box_widget.setLayout(self.ROI_view_box_layout)
        # Creating the preview
        self.preview_box_layout = QVBoxLayout()
        self.preview_box_label = QLabel()
        self.preview_box_layout.addWidget(self.preview_box_label)
        self.preview_box_layout.addWidget(self.dicom_preview)
        self.preview_box_widget = QWidget()
        self.preview_box_widget.setLayout(self.preview_box_layout)

        # Add View and Slider into horizontal box
        self.manipulate_roi_window_instance_view_box.addWidget(self.ROI_view_box_widget)
        self.manipulate_roi_window_instance_view_box.addWidget(self.preview_box_widget)
        # Create a widget to hold the image slice box
        self.manipulate_roi_window_instance_view_widget = QWidget()
        self.manipulate_roi_window_instance_view_widget.setObjectName(
            "ManipulateRoiWindowInstanceActionWidget")
        self.manipulate_roi_window_instance_view_widget.setLayout(
            self.manipulate_roi_window_instance_view_box)

        # Create a horizontal box for containing the input fields and the viewports
        self.manipulate_roi_window_main_box = QHBoxLayout()
        self.manipulate_roi_window_main_box.setObjectName("ManipulateRoiWindowMainBox")
        self.manipulate_roi_window_main_box.addLayout(self.manipulate_roi_window_input_container_box, 1)
        self.manipulate_roi_window_main_box.addWidget(self.manipulate_roi_window_instance_view_widget, 11)

        # Create a new central widget to hold the horizontal box layout
        self.manipulate_roi_window_instance_central_widget = QWidget()
        self.manipulate_roi_window_instance_central_widget.setObjectName("ManipulateRoiWindowInstanceCentralWidget")
        self.manipulate_roi_window_instance_central_widget.setLayout(self.manipulate_roi_window_main_box)

        self.retranslate_ui(self.manipulate_roi_window_instance)
        self.manipulate_roi_window_instance.setStyleSheet(stylesheet)
        self.manipulate_roi_window_instance.setCentralWidget(self.manipulate_roi_window_instance_central_widget)
        QtCore.QMetaObject.connectSlotsByName(self.manipulate_roi_window_instance)

    def onCancelButtonClicked(self):
        """
        This function is used for canceling the drawing
        """
        self.close()

    def onDrawButtonClicked(self):
        """
        Function triggered when the Draw button is pressed from the menu.
        """
        print("Draw pressed")

    def onSaveClicked(self):
        print("Save pressed")

    def set_selected_roi_name(self, roi_name):

        roi_exists = False

        patient_dict_container = PatientDictContainer()
        existing_rois = patient_dict_container.get("rois")

        # Check to see if the ROI already exists
        for key, value in existing_rois.items():
            if roi_name in value['name']:
                roi_exists = True

        if roi_exists:
            QMessageBox.about(self.manipulate_roi_window_instance, "ROI already exists in RTSS",
                              "Would you like to continue?")

        self.ROI_name = roi_name
        self.new_roi_name_line_edit.setText(self.ROI_name)

    def operation_changed(self):
        selected_operation = self.operation_name_dropdown_list.currentText()
        if selected_operation in self.single_roi_operation_names:
            self.second_roi_name_label.setVisible(False)
            self.second_roi_name_dropdown_list.setVisible(False)
            self.margin_label.setVisible(True)
            self.margin_line_edit.setVisible(True)
        else:
            self.second_roi_name_label.setVisible(True)
            self.second_roi_name_dropdown_list.setVisible(True)
            self.margin_label.setVisible(False)
            self.margin_line_edit.setVisible(False)

class SaveROIProgressWindow(QtWidgets.QDialog):
    """
    This class displays a window that advises the user that the RTSTRUCT is being modified, and then creates a new
    thread where the new RTSTRUCT is modified.
    """

    signal_roi_saved = QtCore.Signal(pydicom.Dataset)   # Emits the new dataset

    def __init__(self, *args, **kwargs):
        super(SaveROIProgressWindow, self).__init__(*args, **kwargs)
        layout = QtWidgets.QVBoxLayout()
        text = QtWidgets.QLabel("Creating ROI...")
        layout.addWidget(text)
        self.setWindowTitle("Please wait...")
        self.setFixedWidth(150)
        self.setLayout(layout)

        self.threadpool = QtCore.QThreadPool()

    def start_saving(self, dataset_rtss, roi_name, single_array, ds):
        """
        Creates a thread that generates the new dataset object.
        :param dataset_rtss: dataset of RTSS
        :param roi_name: ROIName
        :param single_array: Coordinates of pixels for new ROI
        :param ds: Data Set of selected DICOM image file
        """
        worker = Worker(ROI.create_roi, dataset_rtss, roi_name, single_array, ds)
        worker.signals.result.connect(self.roi_saved)
        self.threadpool.start(worker)

    def roi_saved(self, result):
        """
        This method is called when the second thread completes generation of the new dataset object.
        :param result: The resulting dataset from the ROI.create_roi function.
        """
        self.signal_roi_saved.emit(result)
        self.close()
